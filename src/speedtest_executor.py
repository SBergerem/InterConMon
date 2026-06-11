from app_settings import SpeedTestSettings
from models import SpeedTestResult, SpeedTestTool
from exceptions import CustomException
from speedtests.base_speed_test import BaseSpeedTest
from speedtests.unknown_speed_test import UnknownSpeedTest


class SpeedTestExecutor:

    def _get_selected_speed_test(self) -> BaseSpeedTest:
        tool: SpeedTestTool = self._settings.get_tool()

        match tool:
            case SpeedTestTool.UNKNOWN:
                return UnknownSpeedTest()
            case _:
                raise CustomException(
                    "SpeedTestExecutor",
                    "_get_selected_speed_test",
                    f"Can't start external speedtest. The configured speedtest cli is unknown: {tool}",
                )

    def __init__(self, settings: SpeedTestSettings) -> None:
        self._settings: SpeedTestSettings = settings

    def run(self) -> SpeedTestResult:
        speed_test: BaseSpeedTest = self._get_selected_speed_test()
        return speed_test.execute()
