# InterConMon – Homelab Internet Monitor

InterConMon is a Docker-based learning project for monitoring internet connection stability in a homelab environment.

The goal of this project is to build a small service that can regularly check the internet connection, detect possible outages, store monitoring data, and provide useful reports through a local web interface.

This project is intentionally developed step by step as a learning project. The focus is not only on building a working tool, but also on understanding the logic, structure, data storage, security considerations, and deployment of a small monitoring service.

---

## Project Status

This project is currently in early development.

The exact implementation details are still being planned and built step by step.

---

## Motivation

This project was started because of recurring stability issues with my current internet connection. Instead of only relying on subjective impressions, I wanted to build a small tool that can collect useful connection data over time.

The goal is to better understand when connection problems happen, how often they occur, and how long they last.

At the same time, this project is used as a practical learning project for programming, Docker, monitoring, databases, web development, and homelab infrastructure.

---

## Goals

The project should eventually be able to:

* Check whether the internet connection is available
* Measure connection quality, for example latency
* Detect internet outages
* Store monitoring data in a database
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
* Logging and storing measured data
* Designing a simple database structure
* Working with SQLite as a lightweight local database
* Structuring a small software project
* Building a local web interface
* Implementing basic authentication and session handling
* Creating browser-based file exports
* Running an application inside Docker
* Using Docker Compose for deployment
* Keeping configuration separate from source code
* Writing useful documentation for a GitHub project

---

## Planned Architecture

The project is planned as a small multi-component application.

The main parts are:

* A monitoring component that checks the internet connection
* A SQLite database component that stores measured data, outage history, logs, and settings
* A web interface for status information, settings, login, and exports
* An export component for creating PDF and Excel files on demand
* Docker support for easier deployment

The exact structure will be developed step by step.

---

## Planned Data Storage

The project is planned to use SQLite for storing monitoring data, detected outages, logs, and application settings.

SQLite was chosen because InterConMon is intended to be a small local homelab tool. It does not require a separate database server, is easy to deploy, and stores the data in a local database file that can be persisted through Docker volumes.

The database may later store information such as:

* Connection checks
* Latency measurements
* Detected outages
* Application/event logs
* Speed test results
* Application settings
* User/login information
* Session data

The exact database schema is not finalized yet and will be designed during development.

---

## Planned Web Interface

The project should include a local web interface.

The web interface should eventually allow users to:

* View the current connection status
* View recent measurements
* View detected outages
* Change monitoring settings
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
* Environment-based or file-based configuration

The exact Docker setup will be developed as part of the project.

---

## Planned Project Direction

The project will be built in small steps:

1. Basic connection check
2. Define result structure
3. Design first database tables
4. Add SQLite database initialization
5. Store check results in SQLite
6. Repeated monitoring loop
7. Outage detection logic
8. Basic Docker support
9. Docker Compose deployment with persistent SQLite storage
10. Simple local web interface
11. Settings page
12. First-time password setup
13. Login and session handling
14. Browser-based PDF and Excel export
15. Documentation and cleanup

The exact file formats, configuration structure, database schema, and output format are not finalized yet.

---

## Privacy and Security

This tool is intended to run locally in a homelab environment.

It should not require public internet access to the service itself.

Configuration files, database contents, and generated monitoring data may contain personal or network-related information and should be handled carefully.

The web interface is intended for local homelab or VPN access only. It should not be exposed directly to the public internet without additional security considerations such as HTTPS, secure reverse proxy configuration, strong authentication, and proper authentication hardening.

Secrets such as database passwords, session secrets, API keys, or other sensitive configuration values should not be committed to the repository.

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

---

## License

This project is licensed under the Apache License 2.0.

You are allowed to use, modify, distribute, fork, and use this project commercially, as long as the license terms are followed.

Please keep a visible attribution to the original project repository:

https://github.com/SBergerem/InterConMon

This software is provided without warranty. The author is not responsible for damages, security issues, data loss, outages, or other problems caused by using, modifying, or deploying this software.
