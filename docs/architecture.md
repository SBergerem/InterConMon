# InterConMon Architecture

InterConMon is a small local internet connection monitoring tool.
It is designed to run continuously, perform regular latency checks, detect outages, store tests in SQLite, and provide structured logs for debugging and later reporting.

## Current Architecture Overview

The current application is split into several focused components:

```text
main.py
→ loads configuration
→ initializes database and logging
→ runs monitoring loop
→ stores latency tests
→ detects outages
→ stores outage information
```

## Components

### NetworkChecker

`NetworkChecker` performs a single latency test against one target.

Current behavior:

* Uses `ping3` on Windows.
* Uses the system `ping` command on Linux and macOS.
* Forces `LC_ALL=C` and `LANG=C` on Linux/macOS to make ping output easier to parse.
* Returns a `LatencyTest`.
* Logs individual ping tests with `detailed_debug`.

### Runner

`Runner` groups multiple latency checks into one test group.

Current behavior:

* Runs latency tests for configured targets.
* Collects all individual `LatencyTest` objects.
* Calculates:

  * `any_success`
  * `group_success`
  * `time_needed_sec`
* Returns a `LatencyTestGroup`.
* Logs group-level execution with `extended_debug`.

### OutageDetector

`OutageDetector` tracks the current connection state.

Current behavior:

* Tracks whether the connection is currently `unknown`, `online`, or `offline`.
* Counts failed latency test groups.
* Starts an outage only after a configured number of failed groups.
* Detects when an outage ends.
* Calculates outage duration.
* Returns an `OutageDetection`.

### AppLogger

`AppLogger` provides structured application logging.

Current behavior:

* Logs to console.
* Can also persist logs into SQLite.
* Supports multiple log levels/detail levels.
* Supports skipping database logging for sensitive internal cases.
* Supports passing an outer cursor to avoid opening nested database connections during active database operations.

Current log levels include:

* `debug`
* `extended_debug`
* `detailed_debug`
* `info`
* `warning`
* `error`
* `critical`

Suggested meaning:

```text
debug
→ normal technical debug information

extended_debug
→ larger internal workflows, for example a full latency test group

detailed_debug
→ very detailed steps, for example each individual ping or SQL statement

info
→ normal important runtime information

warning
→ unusual but recoverable situations

error
→ failed operation

critical
→ severe failure that may stop the program
```

## Database and Repository Layer

The database layer is split into two responsibilities:

### DatabaseManager

The `DatabaseManager` is responsible for the technical database handling only. It manages the database path, opens SQLite connections, enables foreign keys, creates cursors, controls transaction boundaries, commits successful operations, rolls back failed operations and closes connections.

It also owns the database lock to avoid unsafe concurrent write access. Repositories do not open or close database connections themselves.

SQL statement logging is connected through an optional callback. This keeps the database layer independent from the application logger and prevents circular imports.

### Repositories

Repository classes contain the table-specific SQL logic. Each repository is responsible for one area of stored data, for example latency test groups, latency tests, outages, app settings or log entries.

Repositories use the `DatabaseManager` to execute their work inside a transaction. Public `save()` and `load()` methods start their own transaction. Additional `save_in_transaction()` methods can reuse an existing cursor when multiple repository operations must be committed or rolled back together.

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

### latency_tests

Stores individual ping/latency tests.

Example fields:

* `id`
* `group_id`
* `date_time`
* `target`
* `success`
* `latency_ms`
* `error_message`

Each row belongs to a `latency_test_groups` row.

### outages

Stores completed internet outages.

Example fields:

* `id`
* `start_time`
* `end_time`
* `duration_sec`
* `started_group_id`
* `ended_group_id`

### logs

Stores structured application logs.

Example fields:

* `id`
* `date_time`
* `log_level`
* `log_type`
* `log_message`
* `related_object_type`
* `related_object_id`
* `details_json`

### app_settings

Stores application settings as JSON.

Example fields:

* `settings_name`
* `settings_json`
* `changed_at`

Example settings:

```text
latency_test_settings_targets
latency_test_settings_interval_seconds
```

## Runtime Flow

The current monitoring flow is:

```text
1. Load configuration
2. Initialize SQLite database
3. Initialize AppLogger
4. Load application settings
5. Run latency test group
6. Save latency test group and individual tests
7. Pass group to OutageDetector
8. Save outage if one ended
9. Log important events
10. Wait for the next monitoring interval
```

## Important Implementation Notes

### Cursor Handling

Some database operations also create log entries.
To avoid opening nested database connections during an active transaction, some methods pass an existing cursor into the logger.

Important rule:

```text
SELECT:
- execute query
- fetch test
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

### SQL Parameters

SQL values should be passed using placeholders:

```text
VALUES (?, ?, ?)
```

Table names and column names cannot be passed as placeholders.
If they are inserted dynamically, they must only come from trusted internal values or a whitelist.

## Current Status

The current version supports:

* Basic latency monitoring
* SQLite persistence
* Outage detection
* Structured logging
* Database-backed settings
* Multiple debug levels

Future planned features include:

* Local web interface
* Settings management through the web interface
* Authentication and sessions
* Export functions for reports
* Docker deployment
* Optional speed tests
* More detailed reporting
