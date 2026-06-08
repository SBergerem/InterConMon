# InterConMon Architecture

InterConMon is a small local internet connection monitoring tool.
It is designed to run continuously, perform regular latency checks, detect outages, store tests in SQLite, and provide structured logs for debugging and later reporting.

## Current Architecture Overview

The current application is split into several focused components:

```text
main.py
→ loads configuration
→ initializes database and logging
→ loads application settings
→ creates Runner
→ starts Runner

Runner
→ owns monitoring loop
→ runs server latency tests
→ runs gateway latency tests
→ stores latency test groups and individual tests
→ runs outage detection
→ stores completed outage information
```

## Components

### NetworkChecker

`NetworkChecker` performs latency tests.

Current behavior:

* Uses `ping3` on Windows.
* Uses the system `ping` command on Linux and macOS.
* Forces `LC_ALL=C` and `LANG=C` on Linux/macOS to make ping output easier to parse.
* Performs individual latency tests.
* Groups multiple latency tests into a `LatencyTestGroup`.
* Supports different target types through `TestTargetType`.
* Returns `LatencyTest` and `LatencyTestGroup` objects.
* Logs individual ping tests with `detailed_debug`.
* Logs group-level execution with `extended_debug`.

Current target types:

* `server`
* `gateway`

### Runner

`Runner` owns the active monitoring loop.

Current behavior:

* Runs in its own thread.
* Supports clean start and stop behavior.
* Reads settings from `AppSettings`.
* Runs server/internet latency checks.
* Runs gateway/router latency checks.
* Supports separate intervals for server and gateway checks.
* Uses separate `OutageDetector` instances for server and gateway checks.
* Stores latency test groups and individual tests in one shared transaction.
* Triggers outage detection when enabled.
* Stores completed outage records.
* Logs startup, shutdown, monitoring events, and errors.

### OutageDetector

`OutageDetector` tracks connection state for a stream of test groups.

Current behavior:

* Tracks whether the connection is currently `unknown`, `online`, or `offline`.
* Counts failed latency test groups.
* Starts an outage only after a configured number of failed groups.
* Detects when an outage ends.
* Calculates outage duration.
* Returns an `OutageDetection`.
* Stores the test target type in the outage detection result.

The runner currently uses separate `OutageDetector` instances for server checks and gateway checks so that both states can be tracked independently.

### AppSettings

`AppSettings` stores runtime settings in memory.

Current settings groups:

* `LatencyTestSettings`
* `GatewayTestSettings`
* `OutageCheckSettings`

Current setting examples:

```text
latency_test_settings_enabled
latency_test_settings_targets
latency_test_settings_interval_seconds
gateway_test_enabled
gateway_test_targets
gateway_test_interval_seconds
outage_check_enabled
outage_check_max_failed_group_test_count
```

Settings are stored as JSON text in SQLite through `AppSettingsRepository`.

### AppLogger

`AppLogger` provides structured application logging.

Current behavior:

* Logs to console.
* Can also persist logs into SQLite.
* Supports multiple log levels/detail levels.
* Supports skipping database logging for sensitive or early startup cases.
* Supports passing an outer cursor to avoid opening nested database connections during active database operations.

Current log levels include:

* `debug`
* `extended_debug`
* `detailed_debug`
* `info`
* `warning`
* `error`
* `critical`

## Database and Repository Layer

The database layer is split into two responsibilities:

### DatabaseManager

The `DatabaseManager` is responsible for technical database handling only.

Responsibilities:

* Store the database path
* Open SQLite connections
* Enable SQLite foreign keys
* Create cursors
* Control transaction boundaries
* Commit successful operations
* Roll back failed operations
* Close connections
* Own the database lock
* Provide an optional SQL statement logging callback

Repositories do not open or close database connections themselves.

SQL statement logging is connected through an optional callback. This keeps the database layer independent from the application logger and prevents circular imports.

### Repositories

Repository classes contain table-specific SQL logic.

Current repositories include:

* `DatabaseInitializerRepository`
* `LatencyTestGroupRepository`
* `LatencyTestRepository`
* `OutageRepository`
* `LogEntryRepository`
* `AppSettingsRepository`

Repositories use the `DatabaseManager` to execute their work inside a transaction. Public `save()` and `load()` methods usually start their own transaction. Additional `save_in_transaction()` methods can reuse an existing cursor when multiple repository operations must be committed or rolled back together.

For latency monitoring, the latency test group and its individual latency tests are saved in one shared transaction. If saving the individual tests fails, the previously inserted group is rolled back as well. This prevents incomplete measurement data.

The `LogEntryRepository` does not log its own SQL statements, because doing so would create an endless logging loop.

## Database Tables

### latency_test_groups

Stores one group of latency tests.

Example fields:

* `id`
* `start_time`
* `end_time`
* `time_needed_sec`
* `any_success`
* `group_success`
* `test_target_type`

The `test_target_type` field distinguishes between server/internet groups and gateway/router groups.

### latency_tests

Stores individual ping/latency tests.

Example fields:

* `id`
* `group_id`
* `date_time`
* `target`
* `test_target_type`
* `success`
* `latency_ms`
* `error_message`

Each row belongs to a `latency_test_groups` row.

### outages

Stores completed outages.

Example fields:

* `id`
* `connection_state`
* `test_target_type`
* `last_connection_test`
* `change_state`
* `start_time`
* `end_time`
* `duration_sec`
* `started_group_id`
* `ended_group_id`

The `test_target_type` field makes it possible to distinguish between server/internet outages and gateway/router outages.

### logs

Stores structured application logs.

Example fields:

* `id`
* `date_time`
* `log_level`
* `log_type`
* `log_message`
* `class_name`
* `function_name`
* `related_object_type`
* `related_object_id`
* `details_json`

### app_settings

Stores application settings as JSON.

Example fields:

* `settings_name`
* `settings_json`
* `changed_at`

## Runtime Flow

The current monitoring flow is:

```text
1. Load base configuration
2. Initialize SQLite database
3. Initialize AppLogger
4. Load application settings
5. Create Runner
6. Start Runner thread
7. Runner checks whether server tests are due
8. Runner runs server test group if enabled
9. Runner stores server group and tests in one transaction
10. Runner runs server outage detection if enabled
11. Runner checks whether gateway tests are due
12. Runner runs gateway test group if enabled
13. Runner stores gateway group and tests in one transaction
14. Runner runs gateway outage detection if enabled
15. Runner stores outage data if an outage ended
16. Runner waits briefly and repeats
17. Main handles shutdown and saves settings
```

## Important Implementation Notes

### Cursor Handling

Some database operations also create log entries.
To avoid opening nested database connections during an active transaction, some methods pass an existing cursor into the logger.

Important rule:

```text
SELECT:
- execute query
- fetch results
- then log

INSERT:
- execute insert
- store lastrowid
- then log

UPDATE/DELETE:
- execute statement
- store rowcount if needed
- then log
```

This prevents logging from overwriting cursor state such as `fetchall()` results or `lastrowid`.

### Shared Transactions

Some data belongs together and should not be saved partially.

For latency monitoring, this means:

```text
LatencyTestGroup
→ saved first
→ group id is assigned
→ all contained LatencyTest rows receive the group id
→ individual LatencyTest rows are saved
→ commit happens only after both steps succeeded
```

If saving the individual tests fails, the whole transaction is rolled back.

### SQL Statement Logging

Repositories can log SQL statements through `BaseRepository._log_statement()`.
The database manager forwards the log request to a callback that is registered during startup.

This avoids direct imports from the database layer to `AppLogger`.

### SQL Parameters

SQL values should be passed using placeholders:

```text
VALUES (?, ?, ?)
```

Table names and column names cannot be passed as placeholders.
If they are inserted dynamically, they must only come from trusted internal values or a whitelist.

## Current Status

The current version supports:

* Server/internet latency monitoring
* Gateway/router latency monitoring
* Typed test targets
* SQLite persistence
* Shared transactions for grouped latency data
* Outage detection
* Structured logging
* SQL statement logging through callback
* Database-backed settings
* Multiple debug levels
* Runner thread with clean start/stop behavior

Future planned features include:

* Local web interface
* Settings management through the web interface
* Authentication and sessions
* Export functions for reports
* Docker deployment
* Optional speed tests
* More detailed reporting
