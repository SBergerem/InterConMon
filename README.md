# InterConMon – Homelab Internet Monitor

InterConMon is a Docker-oriented learning project for monitoring internet connection stability in a homelab environment.

The goal of this project is to build a small local service that regularly checks connection availability and quality, stores monitoring data, detects outages, and later provides useful reports through a local web interface.

This project is intentionally developed step by step as a learning project. The focus is not only on building a working tool, but also on understanding application structure, monitoring logic, data storage, logging, error handling, security considerations, and deployment of a small homelab service.

---

## Project Status

This project is currently in early development, but the first internal monitoring flow is already working.

The current version already supports:

* Repeated monitoring loop inside `Runner`
* Background runner thread with clean start/stop behavior
* Server/internet latency checks
* Gateway/router latency checks
* Separate test target types for server and gateway checks
* Grouped latency tests
* SQLite database initialization
* Storage of latency test groups and individual latency tests
* Shared transactions for saving a test group and its individual tests together
* Outage detection based on failed test groups
* Separate outage detector instances for server and gateway checks
* Storage of completed outages
* Database-backed application settings
* Structured application logging
* SQL statement logging through a callback
* Multiple debug levels for different levels of detail
* Custom exceptions with class and function context

The local web interface, authentication, exports, Docker setup, and reporting features are planned but not finished yet.

---

## Motivation

This project was started because of recurring stability issues with my current internet connection. Instead of only relying on subjective impressions, I wanted to build a small tool that can collect useful connection data over time.

The goal is to better understand when connection problems happen, how often they occur, and how long they last.

InterConMon is also intended to distinguish between different problem areas. For example, a failed external internet check while the local gateway is still reachable can indicate a different issue than a failed gateway check.

At the same time, this project is used as a practical learning project for programming, Docker, monitoring, databases, web development, logging, and homelab infrastructure.

---

## Goals

The project should eventually be able to:

* Check whether the internet connection is available
* Measure connection quality, for example latency
* Check local gateway/router reachability
* Distinguish between local network/router problems and external internet problems
* Detect internet outages
* Store monitoring data in a database
* Store application settings in the database
* Provide structured application logs
* Provide a local web interface for viewing status and changing settings
* Support password-based login for the web interface
* Use browser sessions/cookies so users do not have to log in every time
* Require password setup or password change on first use
* Generate PDF reports through the web interface
* Generate Excel exports through the web interface
* Allow generated reports/exports to be downloaded directly in the browser
* Run inside Docker
* Be deployable with Docker Compose
* Be understandable and maintainable as a small homelab tool

---

## Learning Goals

This project is also meant to improve practical programming and infrastructure skills.

Important learning topics include:

* Designing a small monitoring service
* Thinking in states, for example online and offline
* Handling repeated checks over time
* Detecting outages based on multiple failed checks
* Distinguishing between different target types
* Logging and storing measured data
* Designing a simple database structure
* Working with SQLite as a lightweight local database
* Using transactions to keep related data consistent
* Storing application settings in a database
* Using JSON for flexible settings storage
* Structuring a small software project
* Avoiding circular imports
* Handling exceptions and error cases cleanly
* Building a local web interface
* Implementing basic authentication and session handling
* Creating browser-based file exports
* Running an application inside Docker
* Using Docker Compose for deployment
* Keeping configuration separate from source code
* Writing useful documentation for a GitHub project

---

## Documentation

Additional technical documentation is available in:

* [`docs/architecture.md`](docs/architecture.md)
* [`docs/roadmap.md`](docs/roadmap.md)

The architecture document describes the current internal structure, major components, database tables, logging concept, runtime flow, repository structure, and important implementation notes.

---

## Current Architecture

InterConMon is currently split into several focused components.

### `main.py`

* prepares and starts the application
* loads configuration
* initializes the database
* initializes logging
* loads application settings
* creates and starts the runner

### `Runner`

* owns the monitoring loop
* runs in its own thread
* starts and stops cleanly
* runs server/internet latency checks
* runs gateway/router latency checks
* saves latency test groups and individual tests
* triggers outage detection
* stores completed outage information

### `NetworkChecker`

* performs individual latency checks
* creates latency test groups
* supports different target types
* uses `ping3` on Windows
* uses the system `ping` command on Linux/macOS

### `OutageDetector`

* tracks connection state
* detects when an outage starts
* detects when an outage ends
* calculates outage duration
* works with typed test groups

### `DatabaseManager`

* handles SQLite connections
* enables SQLite foreign keys
* controls transactions
* commits successful operations
* rolls back failed operations
* owns the database lock
* provides an optional SQL logging callback

### Repository classes

* contain table-specific SQL logic
* save and load latency test groups
* save and load individual latency tests
* save and load outages
* save and load logs
* save and load application settings

### `AppLogger`

* provides structured logging
* writes logs to console
* can write logs to SQLite
* supports multiple debug/detail levels
* avoids circular imports through the database logging callback

### `AppSettings`

* stores runtime settings in memory
* contains latency test settings
* contains gateway test settings
* contains outage check settings
* can serialize settings for database persistence

---

## Logging Concept

InterConMon uses a custom `AppLogger` wrapper around Python logging and SQLite persistence.

The logger supports multiple log levels and detail levels:

* `detailed_debug` – very detailed internal information, for example individual ping tests or SQL statements
* `extended_debug` – larger internal workflows, for example a full latency test group or outage detection run
* `debug` – normal technical debug information
* `info` – normal runtime information
* `warning` – unusual but recoverable situations
* `error` – failed operations
* `critical` – severe failures that may stop the program

Database-internal SQL statement logging is connected through a callback on the `DatabaseManager`. This avoids circular imports between the logger and the database/repository layer.

The `LogEntryRepository` does not log its own SQL statements, because doing so would create an endless logging loop.

Important cursor rule:

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

---

## Planned Data Storage

The project uses SQLite for storing monitoring data, detected outages, logs, and application settings.

SQLite was chosen because InterConMon is intended to be a small local homelab tool. It does not require a separate database server, is easy to deploy, and stores the data in a local database file that can be persisted through Docker volumes.

The database currently includes or is planned to include data such as:

* Latency test groups
* Individual latency measurements
* Test target types, for example server or gateway
* Detected outages
* Application/event logs
* Application settings
* Speed tests
* User/login information
* Session data

Settings are stored as JSON text in SQLite. This keeps the settings system flexible while still keeping the configuration inside the database.

Example setting names:

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

---

## Planned Web Interface

The project should include a local web interface.

The web interface should eventually allow users to:

* View the current connection status
* View recent server/internet measurements
* View recent gateway/router measurements
* View detected outages
* View application logs
* Change monitoring settings
* Change gateway check settings
* Change outage detection settings
* Change logging settings
* Trigger PDF exports
* Trigger Excel exports
* Download generated files directly in the browser

The web interface is intended for local homelab or VPN access only.

---

## Planned Export Functionality

Reports and exports should be generated on demand through the web interface.

The project should eventually support:

* PDF reports for readable summaries
* Excel exports for tabular data analysis
* Browser downloads without manually accessing server files
* Date range selection
* Outage summaries
* Latency statistics
* Separate views for server and gateway checks

The export feature is intended to help review connection problems and share useful information when needed.

---

## Planned Deployment Idea

The application should be able to run inside Docker.

The long-term goal is that someone can deploy it with Docker Compose without needing to manually install many dependencies on the host system.

A future Docker Compose setup may include:

* The InterConMon application container
* A persistent volume for the SQLite database file
* Persistent volumes for configuration and generated exports
* Environment-based or file-based bootstrap configuration

The exact Docker setup will be developed as part of the project.

---

## Planned Project Direction

The project will be built in small steps.

Current and near-term direction:

1. Keep the current monitoring flow stable
2. Continue improving database-backed settings
3. Add local web interface foundation
4. Add settings page for monitoring and gateway settings
5. Add first-time password setup
6. Add login and session handling
7. Add browser-based PDF and Excel export
8. Add basic Docker support
9. Add Docker Compose deployment with persistent SQLite storage
10. Add documentation and cleanup

The exact file formats, configuration structure, database schema, and output formats may still change during development.

---

## Future Runner Direction

The `Runner` is currently the central runtime component.

Current structure:

```text
main.py
→ prepares dependencies
→ initializes database and logging
→ loads settings
→ creates Runner
→ starts Runner

Runner
→ owns monitoring loop
→ runs server latency test groups
→ runs gateway latency test groups
→ stores tests
→ triggers outage detection
→ stores outage data
→ waits for the next interval
→ stops cleanly when requested
```

Later, the `Runner` is intended to run alongside a local web interface. Runtime settings should eventually be changeable through the web interface.

---

## Privacy and Security

This tool is intended to run locally in a homelab environment.

It should not require public internet access to the service itself.

Configuration files, database contents, logs, and generated monitoring data may contain personal or network-related information and should be handled carefully.

The web interface is intended for local homelab or VPN access only. It should not be exposed directly to the public internet without additional security considerations such as HTTPS, secure reverse proxy configuration, strong authentication, and proper authentication hardening.

Secrets such as session secrets, API keys, passwords, or other sensitive configuration values should not be committed to the repository.

---

## Disclaimer

InterConMon is a personal learning and homelab project.

This software is provided "as is", without warranty of any kind. The author does not guarantee that the software is secure, error-free, reliable, or suitable for any specific purpose.

Use this software at your own risk. The author is not responsible for any damages, data loss, security issues, outages, misconfigurations, or other problems that may occur from using, modifying, deploying, or redistributing this software.

The web interface is intended for local network or VPN access only. It should not be exposed directly to the public internet without proper security hardening, such as HTTPS, secure reverse proxy configuration, strong authentication, and additional security review.

This project is not intended to replace professional monitoring, security, or network diagnostic tools.

---

## Repository Purpose

This repository is part of a personal learning and portfolio project.

It is meant to demonstrate practical work with:

* Programming
* Basic network monitoring
* Database-backed application design
* SQLite
* Repository-based persistence
* Web development
* Authentication basics
* Browser-based exports
* Docker
* Docker Compose
* Linux server usage
* Homelab infrastructure
* Documentation
* Step-by-step software development
* Event logging
* Outage detection and persistence
* Settings persistence
* Structured application architecture

---

## License

This project is licensed under the Apache License 2.0.

You are allowed to use, modify, distribute, fork, and use this project commercially, as long as the license terms are followed.

Please keep a visible attribution to the original project repository:

https://github.com/SBergerem/InterConMon

This software is provided without warranty. The author is not responsible for damages, security issues, data loss, outages, or other problems caused by using, modifying, or deploying this software.
