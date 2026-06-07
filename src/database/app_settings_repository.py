from database.base_repository import BaseRepository
from sqlite3 import Cursor
import json
from datetime import datetime
from typing import Any
from app_settings import AppSettings


class AppSettingsRepository(BaseRepository):

    def _save_internal(self, cursor: Cursor, app_settings: AppSettings) -> None:
        for setting_name, settings in app_settings.get_as_dict():
            if self._check_for_existing_tuple("AppSettingsRepository", "app_settings", "settings_name", setting_name, cursor):
                sql = """
                    UPDATE app_settings SET settings_json = ?, changed_at = ? WHERE settings_name = ?
                """

                params: tuple[str, str, str] = (
                    json.dumps(settings),
                    datetime.now().isoformat(),
                    setting_name,
                )

                cursor.execute(sql, params)
                self._log_statement(
                    "AppSettingsRepository",
                    "save",
                    cursor,
                    {"sql": sql, "params": params},
                )
            else:
                sql = """
                    INSERT INTO app_settings (settings_name, settings_json, changed_at)
                    VALUES (?, ?, ?)
                """

                params = (
                    setting_name,
                    json.dumps(settings),
                    datetime.now().isoformat(),
                )

                cursor.execute(sql, params)
                self._log_statement(
                    "AppSettingsRepository",
                    "save",
                    cursor,
                    {"sql": sql, "params": params},
                )

    def _load_internal(self, cursor: Cursor) -> AppSettings:
        sql: str = """
            SELECT settings_name, settings_json FROM app_settings
        """

        cursor.execute(sql)
        rows: list[Any] = cursor.fetchall()

        self._log_statement(
            "AppSettingsRepository",
            "load",
            cursor,
            {"sql": sql, "params": {}, "row_count": len(rows)},
        )

        result: AppSettings = AppSettings()
        for settings_name, settings_json in rows:
            result.add_from_strings(settings_name, settings_json)

        return result

    def save(self, app_settings: AppSettings) -> None:
        self._database_manager.run_in_transaction(lambda cursor: self._save_internal(cursor, app_settings))

    def load(self) -> AppSettings:
        return self._database_manager.run_in_transaction(lambda cursor: self._load_internal(cursor))
