# InterConMon Roadmap

This roadmap describes the planned development direction of InterConMon.

The project is developed step by step as a learning and homelab project. The order may change during development, but the roadmap gives a general direction.

---

## Phase 1 – Core Monitoring Foundation

Goal: Build the basic monitoring logic and store results reliably.

Status: Mostly in progress / partially completed.

Tasks:

* Basic latency check
* Platform-specific ping handling
  * Windows with `ping3`
  * Linux/macOS with system `ping`
* Result models for latency tests
* Group multiple latency tests into one test group
* Store latency test groups in SQLite
* Store individual latency test results in SQLite
* Add basic repeated monitoring flow
* Add outage detection logic
* Store completed outages in SQLite
* Add structured application logging
* Add first database-backed application settings support

---

## Phase 2 – Internal Architecture Cleanup

Goal: Make the internal structure cleaner before adding bigger features.

Tasks:

* Clean up component responsibilities
* Keep startup, runtime, persistence, logging, and settings logic clearly separated
* Prepare the codebase for moving the monitoring loop into `Runner`
* Reduce static/class-based structure where real object state is useful
* Clean up dependency flow between components
* Avoid circular imports
* Improve exception handling
* Keep Pylance/type checking clean
* Improve internal documentation

Planned direction:

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
→ stores results
→ triggers outage detection
→ stores outage data
→ waits for next interval
```

---

## Phase 3 – Settings System

Goal: Make runtime settings configurable and persistent.

Tasks:

* Store monitoring settings in SQLite
* Load settings on application startup
* Save changed settings back to SQLite
* Add default settings when no settings exist
* Add settings for latency targets
* Add settings for monitoring interval
* Add settings for outage detection threshold
* Add settings for logging levels
* Validate loaded settings
* Handle corrupted or missing settings safely

Example planned settings:

```text
latency_test_settings_targets
latency_test_settings_interval_seconds
outage_detection_max_failed_group_test_count
logging_enabled_console_levels
logging_enabled_database_levels
```

---

## Phase 4 – Runner and Background Runtime

Goal: Move the active monitoring runtime out of `main.py` and into `Runner`.

At the moment, parts of the monitoring flow are still controlled directly by `main.py`. In the long term, `main.py` should mainly prepare the application and start the runtime. The `Runner` should become responsible for the repeated monitoring loop.

Planned direction:

```text
main.py
→ load base configuration
→ initialize database
→ initialize logger
→ load application settings
→ create Runner
→ start Runner
→ handle shutdown

Runner
→ run monitoring loop
→ load or receive current settings
→ run latency test groups
→ store latency results
→ call OutageDetector
→ store outage information
→ wait for the next interval
→ stop cleanly when requested
```

Tasks:

* Move repeated monitoring loop logic from `main.py` into `Runner`
* Add a clear `run()` method to `Runner`
* Add a clean stopping mechanism, for example `stop()`
* Keep `main.py` focused on startup and shutdown
* Make `Runner` use database-backed settings
* Make `Runner` use configured latency targets
* Make `Runner` use configured monitoring interval
* Make `Runner` use configured outage detection settings
* Ensure `KeyboardInterrupt` can stop the application cleanly
* Prepare the structure for a later background thread
* Avoid adding thread complexity before the normal runner flow is stable

Later, the `Runner` may run in its own background thread so that the monitoring loop can run alongside the local web interface.

---

## Phase 5 – Local Web Interface

Goal: Add a browser-based interface for local use.

Tasks:

* Add simple local web server
* Show current monitoring status
* Show recent latency test groups
* Show recent outages
* Show application logs
* Add basic settings page
* Allow changing latency targets
* Allow changing monitoring interval
* Allow changing outage detection settings
* Allow changing logging settings

The web interface is intended for local network or VPN access only.

---

## Phase 6 – Authentication and Sessions

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

## Phase 7 – Reports and Exports

Goal: Make collected monitoring data easier to review and share.

Tasks:

* Add PDF report generation
* Add Excel export generation
* Generate reports on demand through the web interface
* Allow direct browser download
* Add date range selection
* Include outage summaries
* Include latency statistics
* Include relevant logs or notes
* Avoid automatically generating unnecessary files in the background

Planned export types:

* PDF summary report
* Excel data export

---

## Phase 8 – Extended Monitoring

Goal: Add more useful checks beyond simple external ping tests.

Tasks:

* Add router/gateway reachability checks
* Distinguish between local network problems and external internet problems
* Add multiple target groups
* Add optional DNS checks
* Add optional HTTP checks
* Add optional speed test support
* Investigate possible official integration options with external measurement tools, if appropriate

Important note:

Any integration with official broadband measurement tools should only be done through supported or allowed interfaces. The project should not bypass measurement rules or automate tools in an unsupported way.

---

## Phase 9 – Reporting Dashboard

Goal: Make the collected data easier to understand.

Tasks:

* Add dashboard overview
* Show current connection state
* Show recent outages
* Show uptime/downtime summary
* Show average latency
* Show highest latency
* Show failed checks
* Add simple charts
* Add filters by date/time range
* Add export buttons from dashboard views

---

## Phase 10 – Docker Support

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

## Phase 11 – Cleanup and Release Preparation

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

These ideas are not part of the immediate scope and may or may not be implemented.

---

## Current Priority

The current priority is:

1. Keep the existing monitoring flow stable
2. Finish database-backed settings
3. Move the monitoring loop into `Runner`
4. Keep `main.py` focused on startup
5. Prepare clean start/stop behavior for the monitoring loop
6. Build the local web interface foundation
7. Add authentication, settings management, and exports
8. Add Docker support after the application structure is clearer

