from backend.settings.app_settings import SpeedTestSettings
from backend.models.models import SpeedTestResult, SpeedTestTool
from backend.exceptions.exceptions import CustomException
from backend.scanning.speedtests.base_speed_test import BaseSpeedTest
from backend.scanning.speedtests.unknown_speed_test import UnknownSpeedTest
from backend.scanning.speedtests.librespeed_speed_test import LibreSpeedSpeedTest


class SpeedTestExecutor:

    def _get_selected_speed_test(self) -> BaseSpeedTest:
        tool: SpeedTestTool = self._settings.get_tool()

        match tool:
            case SpeedTestTool.UNKNOWN:
                return UnknownSpeedTest(self._settings)
            case SpeedTestTool.LIBRESPEED_CLI:
                return LibreSpeedSpeedTest(self._settings)
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
