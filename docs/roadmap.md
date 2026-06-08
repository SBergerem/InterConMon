# InterConMon Roadmap

This roadmap describes the planned development direction of InterConMon.

The project is developed step by step as a learning and homelab project. The order may change during development, but the roadmap gives a general direction.

---

## Phase 1 – Core Monitoring Foundation

Goal: Build the basic monitoring logic and store tests reliably.

Status: Mostly completed.

Completed:

* Basic latency check
* Platform-specific ping handling
  * Windows with `ping3`
  * Linux/macOS with system `ping`
* Models for latency tests
* Group multiple latency tests into one test group
* Store latency test groups in SQLite
* Store individual latency tests in SQLite
* Add basic repeated monitoring flow
* Add outage detection logic
* Store completed outages in SQLite
* Add structured application logging
* Add first database-backed application settings support

Still possible later:

* Improve validation around settings and loaded database values
* Add more tests around outage edge cases
* Add migration strategy for schema changes

---

## Phase 2 – Internal Architecture Cleanup

Goal: Make the internal structure cleaner before adding bigger features.

Status: Mostly completed for the current development stage.

Completed:

* Cleaner component responsibilities
* `main.py` focuses on startup and shutdown
* `Runner` owns the monitoring loop
* Database-specific SQL logic moved into repositories
* `DatabaseManager` reduced to connection, transaction, lock, rollback and callback handling
* Shared transaction handling for latency test groups and their individual tests
* SQL statement logging through callback to avoid circular imports
* `LogEntryRepository` avoids logging itself to prevent logging recursion
* Improved custom exception handling with class and function context
* Cleaner start/stop behavior for the runner thread

Ongoing:

* Continue keeping dependency flow clean
* Keep Pylance/type checking clean
* Improve internal documentation as the project grows
* Avoid unnecessary abstractions until the project actually needs them

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
→ runs test groups
→ stores tests
→ triggers outage detection
→ stores outage data
→ waits for next interval
```

---

## Phase 3 – Settings System

Goal: Make runtime settings configurable and persistent.

Status: In progress / partially completed.

Completed:

* Store monitoring settings in SQLite
* Load settings on application startup
* Save settings back to SQLite on shutdown
* Add settings for server latency checks
* Add settings for gateway checks
* Add settings for monitoring intervals
* Add settings for outage detection threshold
* Add enabled/disabled flags for checks
* Store settings as JSON text in SQLite

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

Still planned:

* Add settings for logging levels through the runtime settings system
* Add default settings when no settings exist
* Validate loaded settings more strictly
* Handle corrupted or missing settings safely
* Prepare settings for editing through the web interface

---

## Phase 4 – Runner and Background Runtime

Goal: Move the active monitoring runtime out of `main.py` and into `Runner`.

Status: Mostly completed.

Completed:

* Monitoring loop moved into `Runner`
* `Runner.run()` starts the monitoring thread
* `Runner.stop()` requests shutdown and joins the thread
* `main.py` handles startup and shutdown
* `Runner` uses database-backed settings
* `Runner` uses configured server latency targets
* `Runner` uses configured gateway targets
* `Runner` uses configured monitoring intervals
* `Runner` uses configured outage detection settings
* `KeyboardInterrupt` can stop the application cleanly
* Runner structure is ready to run alongside a future web interface

Still planned:

* Connect the future web interface to the existing shared `AppSettings` object
* Persist changed settings after updates from the web interface
* Make the future web server interact safely with the runner
* Improve status reporting from the runner to the future web interface

---

## Phase 5 – Gateway and Target Type Monitoring

Goal: Distinguish external internet checks from local gateway/router checks.

Status: Mostly completed for the first version.

Completed:

* Added `TestTargetType`
* Added server and gateway target types
* Added gateway test settings
* Added separate gateway check interval
* Added gateway enabled/disabled flag
* Extended latency test groups with target type
* Extended individual latency tests with target type
* Extended outage detections with target type
* Added separate runner cycle for gateway checks
* Added separate outage detector instance for gateway checks
* Stored gateway and server checks in the database

Still planned:

* Use gateway state to improve diagnostic interpretation
* Show server vs gateway state separately in the future web interface
* Include target type filters in future reports and exports
* Add automatic gateway detection later if useful and reliable

Example interpretation:

```text
Gateway reachable, external targets fail
→ likely external internet/provider problem

Gateway unreachable
→ likely local network/router problem

Gateway reachable, external targets reachable
→ connection appears healthy
```

---

## Phase 6 – Local Web Interface

Goal: Add a browser-based interface for local use.

Tasks:

* Add simple local web server
* Show current monitoring status
* Show recent server/internet measurements
* Show recent gateway/router measurements
* Show recent outages
* Show application logs
* Add basic settings page
* Allow changing latency targets
* Allow changing gateway targets
* Allow changing monitoring intervals
* Allow changing outage detection settings
* Allow changing logging settings

The web interface is intended for local network or VPN access only.

---

## Phase 7 – Authentication and Sessions

Goal: Protect the local web interface.

Tasks:

* Add password-based login
* Add first-time password setup
* Force password change on first use if needed
* Add session handling
* Use cookies for browser sessions
* Add logout
* Store password hashes securely
* Avoid storing plain-text passwords
* Add basic security documentation

---

## Phase 8 – Reports and Exports

Goal: Make collected monitoring data easier to review and share.

Tasks:

* Add PDF report generation
* Add Excel export generation
* Generate reports on demand through the web interface
* Allow direct browser download
* Add date range selection
* Include outage summaries
* Include latency statistics
* Include server and gateway checks separately
* Include relevant logs or notes
* Avoid automatically generating unnecessary files in the background

Planned export types:

* PDF summary report
* Excel data export

---

## Phase 9 – Extended Monitoring

Goal: Add more useful checks beyond simple ping tests.

Tasks:

* Add optional DNS checks
* Add optional HTTP checks
* Add optional speed test support
* Add multiple target groups
* Add more detailed diagnostic classification
* Investigate possible official integration options with external measurement tools, if appropriate

Important note:

Any integration with official broadband measurement tools should only be done through supported or allowed interfaces. The project should not bypass measurement rules or automate tools in an unsupported way.

---

## Phase 10 – Reporting Dashboard

Goal: Make the collected data easier to understand.

Tasks:

* Add dashboard overview
* Show current server/internet connection state
* Show current gateway/router state
* Show recent outages
* Show uptime/downtime summary
* Show average latency
* Show highest latency
* Show failed checks
* Add simple charts
* Add filters by date/time range
* Add export buttons from dashboard views

---

## Phase 11 – Docker Support

Goal: Make the already working application deployable as a small homelab service.

Docker support is planned for a later stage. The internal application structure, monitoring loop, settings system, web interface, authentication, and export functionality should be mostly clear before Docker deployment is finalized.

Tasks:

* Add Dockerfile
* Add Docker Compose file
* Persist SQLite database through a Docker volume
* Persist generated exports through a Docker volume
* Persist configuration or bootstrap files if needed
* Expose only the local web interface port
* Provide example environment/configuration setup
* Document basic Docker usage
* Document update/restart workflow
* Make sure logs are visible through Docker logs
* Add troubleshooting notes for file permissions and volume paths

---

## Phase 12 – Cleanup and Release Preparation

Goal: Prepare the project for a usable first release.

Tasks:

* Clean up code structure
* Review database schema
* Add migration strategy if needed
* Improve README
* Improve architecture documentation
* Improve setup instructions
* Add screenshots once the web interface exists
* Add example configuration
* Add troubleshooting section
* Add versioning
* Prepare first `v1.0.0` release

---

## Long-Term Ideas

Possible future ideas:

* Notification support
* Email alerts
* Webhook alerts
* Integration with Home Assistant
* More advanced report templates
* Configurable retention policy
* Automatic database cleanup
* Backup/export of SQLite database
* Optional Prometheus/Grafana integration
* Multi-user support
* More detailed network diagnostics
* Tamper-evident data integrity checks

These ideas are not part of the immediate scope and may or may not be implemented.

---

## Current Priority

The current priority is:

1. Keep the existing server and gateway monitoring flow stable
2. Finish the database-backed settings behavior
3. Prepare the local web interface foundation
4. Add a settings page for monitoring, gateway and outage settings
5. Add authentication and session handling
6. Add browser-based PDF and Excel exports
7. Add Docker support after the application structure is clearer
