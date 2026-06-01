from enum import Enum
from datetime import datetime

class ConnectionState(Enum):
    UNKNOWN = "unknown"
    ONLINE = "online"
    OFFLINE = "offline"
    
class OutageState(Enum):
    NONE = "none"
    OUTAGE_STARTED = "outage_started"
    OUTAGE_ENDED = "outage_ended"

class OutageDetector:
    
    def __init__(self, max_failed_group_test_count):
        self._current_connection_state = ConnectionState.UNKNOWN
        self._first_failed_test_time = None
        self._failed_groups_test_count = 0
        self._max_failed_group_test_count = max_failed_group_test_count
        self._state_change_time = None
        
    def process_group_result(self, group_result):    
        test_succeeded = group_result["any_success"]
        last_connection_state = self._current_connection_state
        connection_test_date_time = group_result["end_time"]  
        outage_state = OutageState.NONE
        outage_start_time = None
        outage_end_time = None
        outage_duration = None
             
        if test_succeeded:
            if last_connection_state == ConnectionState.OFFLINE:
                outage_state = OutageState.OUTAGE_ENDED
                outage_start_time = self._state_change_time
                self._state_change_time = connection_test_date_time
                outage_end_time = connection_test_date_time
                outage_duration = (datetime.fromisoformat(outage_end_time) 
                    - datetime.fromisoformat(outage_start_time)).total_seconds()
            
            self._current_connection_state = ConnectionState.ONLINE
            self._first_failed_test_time = None
            self._failed_groups_test_count = 0
        else:
            if self._first_failed_test_time is None:
                self._first_failed_test_time = group_result["start_time"]
            
            self._failed_groups_test_count += 1
            
            if ((last_connection_state != ConnectionState.OFFLINE) 
                and (self._failed_groups_test_count >= self._max_failed_group_test_count)):
                self._current_connection_state = ConnectionState.OFFLINE
                self._state_change_time = self._first_failed_test_time
                outage_state = OutageState.OUTAGE_STARTED
                
        return {
            "connection_state": self._current_connection_state.value,
            "last_connection_test": self._last_connection_test,
            "outage_state": outage_state.value,
            "outage_state_change_time": self._outage_state_change_time,
            "outage_start_time": outage_start_time,
            "outage_end_time": outage_end_time,
            "outage_duration_sec": outage_duration
        }        
            
                