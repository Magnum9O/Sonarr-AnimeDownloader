from .Database import Database

from typing import Literal

class Settings(Database):
	def __getitem__(self, key: Literal["AutoBind","LogLevel","MaxConcurrentDownloads","MoveEp","RenameEp","ScanDelay","TagsMode"]):
		return self._data[key]
	
	def __setitem__(self, key: Literal["AutoBind","LogLevel","MaxConcurrentDownloads","MoveEp","RenameEp","ScanDelay","TagsMode"], value):
		if key not in self._data: raise KeyError(key)

		self._data[key] = value
		self.sync()
	
	def fix(self) -> None:
		defaults = {
			"AutoBind": True,
			"LogLevel": "DEBUG",
			"MaxConcurrentDownloads": 1,
			"MoveEp": True,
			"RenameEp": True,
			"ScanDelay": 30,
			"TagsMode": "WHITELIST"
		}

		if not self.db.exists() or self.db.stat().st_size == 0:
			self.write(defaults)
			return

		current = self.read()
		changed = False
		for key, value in defaults.items():
			if key not in current:
				current[key] = value
				changed = True

		if changed:
			self.write(current)
	
	def __iter__(self):
		for key in self._data:
			yield key
	
	def __len__(self) -> int:
		return len(self._data)
	
	def __contains__(self, key: str):
		"""Controlla se un impostazione esiste."""

		return key in self._data
