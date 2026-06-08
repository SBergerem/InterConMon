# InterConMon – Homelab Internet Monitor

InterConMon is a Docker-oriented learning project for monitoring internet connection stability in a homelab environment.

The goal of this project is to build a small local service that can regularly check the internet connection, detect possible outages, store monitoring data, and later provide useful reports through a local web interface.

This project is intentionally developed step by step as a learning project. The focus is not only on building a working tool, but also on understanding the logic, structure, data storage, logging, security considerations, and deployment of a small monitoring service.

---

## Project Status

This project is currently in early development.

The current version already contains the first working internal monitoring flow:

* Basic latency checks
* Grouped latency tests
* SQLite database initialization
* Storage of latency test groups and individual latency tests
* Outage detection based on failed test groups
* Storage of completed outages
* Database-backed application settings
* Structured application logging
* Multiple debug levels for different levels of detail

The local web interface, authentication, exports, Docker setup, and reporting features are planned but not finished yet.

---

## Motivation

This project was started because of recurring stability issues with my current internet connection. Instead of only relying on subjective impressions, I wanted to build a small tool that can collect useful connection data over time.

The goal is to better understand when connection problems happen, how often they occur, and how long they last.

At the same time, this project is used as a practical learning project for programming, Docker, monitoring, databases, web development, logging, and homelab infrastructure.

---

## Goals

The project should eventually be able to:

* Check whether the internet connection is available
* Measure connection quality, for example latency
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
* Logging and storing measured data
* Designing a simple database structure
* Working with SQLite as a lightweight local database
* Storing application settings in a database
* Using JSON for flexible settings storage
* Structuring a small software project
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

The architecture document describes the current internal structure, major components, database tables, logging concept, runtime flow, and important implementation notes.

---

## Current Architecture

InterConMon is currently split into several focused components.

The most important components are:

* `main.py`

  * prepares and starts the application
  * initializes configuration, database, logger, settings, and monitoring flow

* `Runner`

  * currently runs latency test groups
  * should later own the full monitoring loop
  * should eventually be started by `main.py`, possibly in its own background thread

* `NetworkChecker`

  * performs individual latency checks
  * uses `ping3` on Windows
  * uses the system `ping` command on Linux/macOS

* `OutageDetector`

  * tracks connection state
  * detects when an outage starts
  * detects when an outage ends
  * calculates outage duration

* `DatabaseManager`

  * initializes SQLite tables
  * stores latency test groups
  * stores individual latency tests
  * stores outages
  * stores logs
  * stores and loads application settings

* `AppLogger`

  * provides structured logging
  * writes logs to console
  * can write logs to SQLite
  * supports multiple debug/detail levels

* `AppSettingsManager`

  * converts application settings between Python objects and database rows
  * stores settings as JSON text in SQLite

The long-term direction is that `main.py` should only prepare and start the application, while `Runner` should own the actual monitoring loop.

---

## Logging Concept

InterConMon uses a custom `AppLogger` wrapper around Python logging and SQLite persistence.

The logger supports multiple log levels and detail levels:

* `detailed_debug`

  * very detailed internal information
  * for example individual ping tests or SQL statements

* `extended_debug`

  * larger internal workflows
  * for example a full latency test group or database transaction

* `debug`

  * normal technical debug information

* `info`

  * normal runtime information

* `warning`

  * unusual but recoverable situations

* `error`

  * failed operations

* `critical`

  * severe failures that may stop the program

Database-internal logging is handled carefully because logging itself can also write to the database. In some cases, an existing cursor is passed into logging methods to avoid opening nested database connections.

Important cursor rule:

```text
SELECT:
- execute query
- fetch tests
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

## Planned Architecture

The project is planned as a small multi-component application.

The main parts are:

* A monitoring component that checks the internet connection
* A runner component that owns the monitoring loop
* A SQLite database component that stores measured data, outage history, logs, and settings
* A settings component that loads and stores runtime settings
* A web interface for status information, settings, login, and exports
* An export component for creating PDF and Excel files on demand
* Docker support for easier deployment

The exact structure will continue to be developed step by step.

---

## Planned Data Storage

The project uses SQLite for storing monitoring data, detected outages, logs, and application settings.

SQLite was chosen because InterConMon is intended to be a small local homelab tool. It does not require a separate database server, is easy to deploy, and stores the data in a local database file that can be persisted through Docker volumes.

The database currently includes or is planned to include data such as:

* Latency test groups
* Individual latency measurements
* Detected outages
* Application/event logs
* Application settings
* Speed tests
* User/login information
* Session data

Settings are stored as JSON text in SQLite. This keeps the settings system flexible while still keeping the configuration inside the database.

Example setting names:

```text
latency_test_settings_targets
latency_test_settings_interval_seconds
```

---

## Planned Web Interface

The project should include a local web interface.

The web interface should eventually allow users to:

* View the current connection status
* View recent measurements
* View detected outages
* View application logs
* Change monitoring settings
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

1. Basic connection check
2. Define test structures
3. Design first database tables
4. Add SQLite database initialization
5. Store check tests in SQLite
6. Add structured logging
7. Add database-backed settings
8. Repeated monitoring loop
9. Outage detection logic
10. Move monitoring loop responsibility into `Runner`
11. Prepare `Runner` for clean start/stop behavior
12. Add basic Docker support
13. Add Docker Compose deployment with persistent SQLite storage
14. Add simple local web interface
15. Add settings page
16. Add first-time password setup
17. Add login and session handling
18. Add browser-based PDF and Excel export
19. Add documentation and cleanup

The exact file formats, configuration structure, database schema, and output formats may still change during development.

---

## Future Runner Direction

The `Runner` should eventually become the central runtime component.

The intended long-term structure is:

```text
main.py
→ prepares dependencies
→ initializes database and logging
→ loads settings
→ creates Runner
→ starts Runner

Runner
→ owns monitoring loop
→ runs latency test groups
→ stores tests
→ triggers outage detection
→ stores outage data
→ waits for the next interval
```

Later, the `Runner` may run in its own background thread so that the monitoring loop can run alongside a local web interface.

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
