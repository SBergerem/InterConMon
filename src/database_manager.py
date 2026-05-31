from pathlib import Path
import sqlite3

class DatabaseManager:
    
    def __init__(self, database_path):
        self._database_path = Path(database_path)
        self._database_path.parent.mkdir(parents=True, exist_ok=True)        
        self._connection = None
        
    def _open_connection(self):
        self._connection = sqlite3.connect(self._database_path)
        cursor = self._connection.cursor()
        cursor.execute("PRAGMA foreign_keys = ON")
        return cursor
    
    def _close_connection(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None
    
    def initialize_database(self):        
        try:
            cursor = self._open_connection()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS latency_test_groups(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    time_needed_sec REAL NOT NULL,
                    any_success INTEGER NOT NULL,
                    group_success INTEGER NOT NULL 
                )
            """)
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS latency_tests(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    group_id INTEGER NOT NULL,
                    date_time TEXT NOT NULL,
                    target TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    latency_ms REAL,
                    error_message TEXT,
                    
                    FOREIGN KEY (group_id) REFERENCES latency_test_groups(id)
                    ON DELETE CASCADE
                )               
            """)
            
            self._connection.commit()
        finally:
            self._close_connection()
            
    
    def save_latency_group(self, latency_group):
        try:
            cursor = self._open_connection()
            
            cursor.execute("""
                INSERT INTO latency_test_groups (start_time, end_time, time_needed_sec, any_success, group_success) 
                VALUES (?, ?, ?, ?, ?)
            """, (latency_group["start_time"], latency_group["end_time"], latency_group["time_needed_sec"], int(latency_group["any_success"]), int(latency_group["group_success"])))
            
            group_id = cursor.lastrowid
            
            for test_result in latency_group["test_results"]:
                cursor.execute("""
                    INSERT INTO latency_tests (group_id, date_time, target, success, latency_ms, error_message)  
                    VALUES (?, ?, ?, ?, ?, ?)                 
                """, (group_id, test_result["date_time"], test_result["target"], int(test_result["success"]), test_result["latency_ms"], test_result["error_message"]))
                
            self._connection.commit()
        except:
            self._connection.rollback()
        finally:
            self._close_connection()
        
        
    