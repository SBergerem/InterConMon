from models.models import SpeedTestResult
from api.schemas.speed_test_schema import SpeedTestResponse, SpeedTestListResponse


class SpeedTestMapper:

    @classmethod
    def map_speed_test_to_response(cls, speed_test: SpeedTestResult | None) -> SpeedTestResponse | None:
        if speed_test is None:
            return None
        else:
            return SpeedTestResponse(
                id=speed_test.id,
                date_time=speed_test.date_time,
                success=speed_test.success,
                download_mbps=speed_test.download_mbps,
                upload_mbps=speed_test.upload_mbps,
                ping_ms=speed_test.ping_ms,
                jitter_ms=speed_test.jitter_ms,
                server_name=speed_test.server_name,
                server_location=speed_test.server_location,
                server_id=speed_test.server_id,
                server_url=speed_test.server_url,
                isp=speed_test.isp,
                external_ip=speed_test.external_ip,
                error_message=speed_test.error_message,
                duration_sec=speed_test.duration_sec,
                tool=speed_test.tool.value,
            )

    @classmethod
    def map_speed_tests_to_response(cls, speed_tests: list[SpeedTestResult] | None) -> SpeedTestListResponse:
        if speed_tests is None or len(speed_tests) == 0:
            return SpeedTestListResponse(items=None)
        else:
            responses: list[SpeedTestResponse | None] = []
            for speed_test in speed_tests:
                responses.append(cls.map_speed_test_to_response(speed_test))

            return SpeedTestListResponse(items=responses)
