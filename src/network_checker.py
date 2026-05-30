import platform
import subprocess
import os
import re
from ping3 import ping

class NetworkChecker:
    
    def __init__(self):
        pass
    
    def test_latency(self, target):
        result = {
            "target": target,
            "success": None,
            "latency_ms": None,
            "error_message": None
        }
          
        try:
            system = platform.system()
            
            ping_result = None  
            
            if system == "Windows":
                latency = ping(target, unit="ms")
                
                if isinstance(latency, (int, float)) and not isinstance(latency, bool):
                    result["success"] = True
                    result["latency_ms"] = latency
                else:
                    result["success"] = False
                                    
            elif system in ["Linux", "Darwin"]:
                env = os.environ.copy()
                env["LC_ALL"] = "C"
                env["LANG"] = "C"
                ping_result = subprocess.run(
                    ["ping", "-c", "1",  target],
                    capture_output=True,
                    text=True,
                    timeout=5,
                    encoding="utf-8",
                    errors="replace",
                    env=env
                )
                
                if ping_result.returncode == 0:
                    latency_text = re.search(r"time=\s*([0-9]+(?:\.[0-9]+)?)\s*ms", ping_result.stdout)
                    
                    result["success"] = True
                    
                    if latency_text is not None:
                        result["latency_ms"] = float(latency_text.group(1))
                    else:
                        result["latency_ms"] = None
                        result["error_message"] = ping_result.stderr
                else:
                    result["success"] = False
                    
            else:
                result["success"] = False
                result["error_message"] = "Error: Can't ping. OS unknown"
    
        except Exception as ex:
            result["success"] = False
            result["error_message"] = ex
            
        return result
            