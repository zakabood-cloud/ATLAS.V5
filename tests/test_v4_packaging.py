import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from atlas.io import AtlasError
from scripts.package_release import verify_zip
from scripts.release_common import input_inventory, release_files, verify_input_inventory

ROOT = Path(__file__).resolve().parents[1]


class ReleasePayloadTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(dir=ROOT)
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, name, content="x"):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_explicit_payload_excludes_private_and_generated_data(self):
        for name in (
            "README.md", "AGENTS.md", "pyproject.toml", "memory/README.md",
            "memory/history/old.json", "memory/secret.json", "projects/client/state.json",
            ".env", ".env.local", ".mcp.json", "settings.local.json",
            "reports/credentials.json", "scripts/server.pem",
            "releases/ATLAS.zip", "scripts/tool.py", "reports/V4_REVIEW.md", "research/log.json", "projects/.gitkeep",
            "reports/test_results.json", "reports/package_validation.json",
        ):
            self.write(name)
        included = {path.relative_to(self.root).as_posix() for path in release_files(self.root)}
        self.assertIn("README.md", included)
        self.assertIn("memory/README.md", included)
        self.assertIn("scripts/tool.py", included)
        self.assertIn("reports/V4_REVIEW.md", included)
        self.assertIn("research/log.json", included)
        self.assertIn("projects/.gitkeep", included)
        self.assertIn("reports/test_results.json", included)
        self.assertIn("reports/package_validation.json", included)
        inventory = input_inventory(self.root)
        self.assertNotIn("reports/test_results.json", inventory)
        self.assertNotIn("reports/package_validation.json", inventory)
        for excluded in (
            "memory/history/old.json", "memory/secret.json", "projects/client/state.json",
            ".env", ".env.local", ".mcp.json", "settings.local.json",
            "reports/credentials.json", "scripts/server.pem",
            "releases/ATLAS.zip",
        ):
            self.assertNotIn(excluded, included)

    def test_symlinks_are_rejected(self):
        self.write("scripts/actual.py")
        (self.root / "scripts/link.py").symlink_to(self.root / "scripts/actual.py")
        with self.assertRaises(AtlasError):
            release_files(self.root)

    def test_validated_inventory_detects_change_addition_and_deletion(self):
        self.write("README.md", "first")
        self.write("scripts/one.py", "one")
        recorded = input_inventory(self.root)
        verify_input_inventory(recorded, self.root)
        self.write("scripts/one.py", "changed")
        with self.assertRaises(AtlasError):
            verify_input_inventory(recorded, self.root)
        self.write("scripts/one.py", "one")
        self.write("scripts/two.py", "two")
        with self.assertRaises(AtlasError):
            verify_input_inventory(recorded, self.root)
        (self.root / "scripts/two.py").unlink()
        (self.root / "scripts/one.py").unlink()
        with self.assertRaises(AtlasError):
            verify_input_inventory(recorded, self.root)

    def test_raw_zip_extra_member_is_not_hidden_by_manifest_filtering(self):
        archive_path = self.root / "extra.zip"
        extraction = self.root / "extracted"
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr("ATLAS/release_manifest.json", json.dumps({
                "schema_version": 1, "hash_algorithm": "SHA-256", "files": [],
            }))
            archive.writestr("ATLAS/unlisted.txt", "smuggled")
            archive.writestr("ATLAS/unlisted-dir/", "")
        with self.assertRaisesRegex(AtlasError, "member set"):
            verify_zip(archive_path, extraction)

    def test_unsafe_zip_member_is_rejected_before_extraction(self):
        archive_path = self.root / "unsafe.zip"
        with zipfile.ZipFile(archive_path, "w") as archive:
            archive.writestr("ATLAS/../outside.txt", "unsafe")
        with self.assertRaises(AtlasError):
            verify_zip(archive_path, self.root / "unsafe-extract")


if __name__ == "__main__":
    unittest.main()
