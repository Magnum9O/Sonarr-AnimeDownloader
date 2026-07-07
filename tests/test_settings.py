import json
import tempfile
import pathlib
import unittest
import importlib.util
import sys
import types

ROOT = pathlib.Path(__file__).resolve().parents[1]
DATABASE_DIR = ROOT.joinpath("src", "components", "backend", "database")


def load_settings_class():
	package_names = [
		"src",
		"src.components",
		"src.components.backend",
		"src.components.backend.database",
	]
	for name in package_names:
		if name not in sys.modules:
			module = types.ModuleType(name)
			module.__path__ = []
			sys.modules[name] = module

	for module_name in ["Database", "Settings"]:
		full_name = f"src.components.backend.database.{module_name}"
		if full_name in sys.modules:
			continue

		spec = importlib.util.spec_from_file_location(
			full_name,
			DATABASE_DIR.joinpath(f"{module_name}.py"),
		)
		module = importlib.util.module_from_spec(spec)
		sys.modules[full_name] = module
		spec.loader.exec_module(module)

	return sys.modules["src.components.backend.database.Settings"].Settings


Settings = load_settings_class()


class TestSettingsMigration(unittest.TestCase):
	def test_missing_keys_are_backfilled(self):
		with tempfile.TemporaryDirectory() as tmp:
			db = pathlib.Path(tmp).joinpath("settings.json")
			db.write_text(json.dumps({
				"AutoBind": True,
				"LogLevel": "INFO",
				"MoveEp": True,
				"RenameEp": True,
				"ScanDelay": 30,
				"TagsMode": "BLACKLIST"
			}))

			settings = Settings(db)

			self.assertEqual(settings["MaxConcurrentDownloads"], 1)

			data = json.loads(db.read_text())
			self.assertEqual(data["MaxConcurrentDownloads"], 1)


if __name__ == "__main__":
	unittest.main()
