"""Behavioral checks for static extraction, provenance, offline lookup and contract diffs."""

from contextlib import redirect_stdout
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

import wow_api


DOCUMENT = r'''
-- A brace in a comment must not terminate a table: }
local Demo =
{
    Name = "Demo", Type = "System", Namespace = "C_Demo", Environment = "All",
    Functions = {
        { Name = "Read", Type = "Function", MayReturnNothing = true,
          Documentation = { "quoted \"}\" and comma, stay text" },
          SecretArguments = "AllowedWhenUntainted",
          Arguments = { { Name = "unit", Type = "UnitToken", Nilable = true } },
          Returns = { { Name = "value", Type = "number", Nilable = false } },
        },
    },
    Events = {
        { Name = "Changed", Type = "Event", LiteralName = "DEMO_CHANGED",
          Payload = { { Name = "amount", Type = "number", Nilable = false } },
        },
    },
    Tables = {
        { Name = "DemoChoice", Type = "Enumeration", Fields = {
            { Name = "None", Type = "DemoChoice", EnumValue = -1 },
            { Name = "Other", Type = "DemoChoice", EnumValue = 2 ^ 3 },
        } },
    },
    Predicates = {},
};
APIDocumentation:AddDocumentationTable(Demo);
'''


class ApiToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        cls.repo = cls.root / "source"
        cls.repo.mkdir()
        def git(*args):
            return subprocess.run(["git", "-C", str(cls.repo), *args], check=True, capture_output=True).stdout.decode().strip()
        cls.git = staticmethod(git)
        git("init")
        git("config", "user.email", "api-test@example.invalid")
        git("config", "user.name", "API Tool Test")
        git("remote", "add", "origin", wow_api.REMOTE)
        folder = cls.repo / wow_api.DOC_PATH
        folder.mkdir(parents=True)
        path = folder / "DemoDocumentation.lua"
        path.write_text(DOCUMENT, encoding="utf-8")
        (cls.repo / "version.txt").write_text("12.1.5.1\n", encoding="utf-8")
        git("add", ".")
        git("commit", "-m", "fixture one")
        cls.old_commit = git("rev-parse", "HEAD")
        cls.old = cls.root / "old"
        with redirect_stdout(io.StringIO()):
            wow_api.snapshot(cls.repo, cls.old_commit, "live", "retail", cls.old)
        # Meaningful changes: nested event secrecy and a new restriction; no API rename.
        updated = DOCUMENT.replace('Name = "amount", Type = "number", Nilable = false',
                                   'Name = "amount", Type = "number", Nilable = false, SecretValue = true')
        updated = updated.replace('Name = "Read", Type = "Function",',
                                  'Name = "Read", Type = "Function", HasRestrictions = true,')
        path.write_text("\n\n" + updated, encoding="utf-8")
        (cls.repo / "version.txt").write_text("12.1.5.2\n", encoding="utf-8")
        git("add", ".")
        git("commit", "-m", "fixture two")
        cls.new = cls.root / "new"
        with redirect_stdout(io.StringIO()):
            wow_api.snapshot(cls.repo, "HEAD", "live", "retail", cls.new)

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_static_table_parser(self):
        rows = wow_api.records_from(wow_api.LuaLiteralParser(DOCUMENT).document(), "DemoDocumentation.lua")
        function = next(r for r in rows if r["kind"] == "function")
        self.assertEqual(function["name"], "C_Demo.Read")
        self.assertTrue(function["contract"]["Arguments"][0]["Nilable"])
        self.assertEqual(function["contract"]["Documentation"], ['quoted "}" and comma, stay text'])
        enum = next(r for r in rows if r["kind"] == "enumeration")
        self.assertEqual(enum["contract"]["Fields"][0]["EnumValue"], -1)
        self.assertEqual(enum["contract"]["Fields"][1]["EnumValue"], {"lua_expression": "2 ^ 3"})

    def test_constants_without_system_name_and_script_methods(self):
        constants = 'local Choices = { Tables = {{Name="Choice",Type="Enumeration",Fields={}}} }; APIDocumentation:AddDocumentationTable(Choices);'
        rows = wow_api.records_from(wow_api.LuaLiteralParser(constants).document(), "Choices.lua")
        self.assertEqual(rows[0]["owner"], "Choices")
        self.assertEqual(rows[1]["name"], "Enum.Choice")
        method = DOCUMENT.replace('Type = "System"', 'Type = "ScriptObject"')
        rows = wow_api.records_from(wow_api.LuaLiteralParser(method).document(), "Demo.lua")
        self.assertIn("Demo:Read", [r["name"] for r in rows if r["kind"] == "method"])

    def test_reject_executable_or_truncated_documentation(self):
        with self.assertRaises(ValueError):
            wow_api.LuaLiteralParser(DOCUMENT + '\nos.execute("anything")').document()
        with self.assertRaises(ValueError):
            wow_api.LuaLiteralParser('local Demo = { Name = "Demo"').document()

    def test_pinned_commit_survives_worktree_changes(self):
        out = self.root / "pinned"
        with redirect_stdout(io.StringIO()):
            wow_api.snapshot(self.repo, self.old_commit, "live", "retail", out)
        meta, rows = wow_api.load_snapshot(out)
        self.assertEqual(meta["build"], "12.1.5.1")
        self.assertEqual(meta["commit"], self.old_commit)
        self.assertFalse(any(r["contract"].get("HasRestrictions") for r in rows))

    def test_nested_secret_and_restriction_delta(self):
        report = wow_api.compare(self.old, self.new)
        self.assertEqual(report["added"], [])
        self.assertEqual(report["removed"], [])
        self.assertEqual(len(report["changed"]), 2)
        paths = [c["path"] for r in report["changed"] for c in r["changes"]]
        self.assertIn("Payload[0].SecretValue", paths)
        self.assertIn("HasRestrictions", paths)
        self.assertEqual(wow_api.compare(self.old, self.old)["changed"], [])

    def test_offline_search_and_nested_enum_name(self):
        output = io.StringIO()
        with redirect_stdout(output):
            status = wow_api.main(["search", "Enum.DemoChoice.None", "--exact", "--index", str(self.new)])
        self.assertEqual(status, 0)
        result = json.loads(output.getvalue())
        self.assertEqual(result["total"], 1)
        self.assertIn(result["commit"], result["results"][0]["source_url"])
        with redirect_stdout(io.StringIO()):
            self.assertEqual(wow_api.main(["search", "NO_SUCH_SYMBOL", "--index", str(self.new)]), 1)

    def test_snapshot_integrity_and_client_separation(self):
        other = self.root / "other-client"
        with redirect_stdout(io.StringIO()):
            wow_api.snapshot(self.repo, "HEAD", "classic", "classic-era", other)
        with self.assertRaisesRegex(ValueError, "different client"):
            wow_api.compare(self.old, other)
        (other / "symbols.jsonl").write_text("{}\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "checksum"):
            wow_api.load_snapshot(other)
        with self.assertRaisesRegex(ValueError, "not empty"):
            wow_api.snapshot(self.repo, "HEAD", "live", "retail", self.old)


if __name__ == "__main__":
    unittest.main()
