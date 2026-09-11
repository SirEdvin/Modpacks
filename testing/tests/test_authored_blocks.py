"""Regression tests for optional block fixtures; no Minecraft runtime needed."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

spec = importlib.util.spec_from_file_location(
    "generator", Path(__file__).parents[1] / "bin/generate-authored-blocks.py"
)
assert spec is not None and spec.loader is not None
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)

OPTIONAL = {"peripheralworks:ae2_pattern_pedestal", "peripheralworks:me_network_peripheral"}
ORDINARY = {"peripheralworks:item_pedestal", "peripheralworks:unexpected_new_block"}


class OptionalBlocksTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.data = Path(self.temp.name)
        self.mods = self.data / "mods"
        self.mods.mkdir()
        with zipfile.ZipFile(self.mods / "peripheralworks-test.jar", "w") as jar:
            jar.writestr("fabric.mod.json", json.dumps({"id": "peripheralworks"}))
            for block in OPTIONAL | ORDINARY:
                namespace, name = block.split(":")
                jar.writestr(f"assets/{namespace}/blockstates/{name}.json", "{}")

    def install_ae2(self, metadata, content):
        with zipfile.ZipFile(self.mods / "ae2-test.jar", "w") as jar:
            jar.writestr(metadata, content)

    def test_optional_blocks_absent_without_ae2(self):
        blocks, jars, _, _ = generator.discover(self.mods)
        self.assertEqual(set(blocks), ORDINARY)
        self.assertEqual(set(jars["peripheralworks-test.jar"]), ORDINARY)

    def test_unknown_blocks_are_not_silently_skipped(self):
        self.assertIn("peripheralworks:unexpected_new_block", generator.discover(self.mods)[0])

    def test_present_ae2_keeps_optional_blocks_for_each_loader(self):
        for metadata, content in [
            ("fabric.mod.json", '{"id":"ae2"}'),
            ("META-INF/mods.toml", '[[mods]]\nmodId="ae2"\n'),
            ("META-INF/neoforge.mods.toml", '[[mods]]\nmodId="ae2"\n'),
        ]:
            with self.subTest(metadata=metadata):
                self.install_ae2(metadata, content)
                self.assertEqual(set(generator.discover(self.mods)[0]), OPTIONAL | ORDINARY)

    def test_dependency_declarations_do_not_count_as_installed_mods(self):
        self.install_ae2("META-INF/neoforge.mods.toml", '''[[mods]]
modId="not_ae2"
[[dependencies.not_ae2]]
modId="ae2"
type="optional"
''')
        self.assertNotIn("ae2", generator.installed_mod_ids(self.mods))
        self.assertEqual(set(generator.discover(self.mods)[0]), ORDINARY)

    def test_manifest_records_skipped_blocks_and_generated_commands_exclude_them(self):
        out = self.data / "output"
        generator.generate("minimal-fabric-1.20", 25574, self.data, out)
        manifest = json.loads((out / "authored-blocks.json").read_text())
        self.assertEqual(manifest.get("skipped_block_count"), 2)
        skipped = manifest["skipped_blocks"]
        self.assertEqual({x["block"] for x in skipped}, OPTIONAL)
        for entry in skipped:
            self.assertEqual(entry["missing_mods"], ["ae2"])
            self.assertEqual(entry["source_jar"], "peripheralworks-test.jar")
        self.assertEqual({cell["block"] for cell in manifest["cells"]}, ORDINARY)
        self.assertTrue(all(entry["reason"] == "optional integration dependency not installed" for entry in skipped))
        commands = (out / "authored-blocks.mcfunction").read_text()
        for block in OPTIONAL:
            self.assertNotIn(block, commands)
        for block in ORDINARY:
            self.assertIn(block, commands)

    def test_present_dependency_has_zero_skips_and_auditable_optional_cells(self):
        self.install_ae2("META-INF/mods.toml", '[[mods]]\nmodId="first_mod"\n[[mods]]\nmodId="ae2"\n')
        out = self.data / "output"
        generator.generate("forge-1.20", 25571, self.data, out)
        manifest = json.loads((out / "authored-blocks.json").read_text())
        self.assertEqual(manifest["skipped_blocks"], [])
        self.assertEqual(manifest["skipped_block_count"], 0)
        self.assertEqual({cell["block"] for cell in manifest["cells"]}, OPTIONAL | ORDINARY)
        commands = (out / "authored-blocks.mcfunction").read_text()
        for block in OPTIONAL:
            self.assertIn(block, commands)

    def test_forge_dependency_only_is_not_installed(self):
        self.install_ae2("META-INF/mods.toml", '[[mods]]\nmodId="other"\n[[dependencies.other]]\nmodId="ae2"\nmandatory=false\n')
        self.assertNotIn("ae2", generator.installed_mod_ids(self.mods))
        self.assertEqual(set(generator.discover(self.mods)[0]), ORDINARY)


if __name__ == "__main__":
    unittest.main()
