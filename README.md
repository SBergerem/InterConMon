# InterConMon – Homelab Internet Monitor

InterConMon is a Docker-based learning project for monitoring internet connection stability in a homelab environment.

The goal of this project is to build a small service that can regularly check the internet connection, detect possible outages, and store useful information about connection quality.

This project is intentionally developed step by step as a learning project. The focus is not only on building a working tool, but also on understanding the logic, structure, and deployment of a small monitoring service.

---

## Disclaimer

InterConMon is a personal learning and homelab project.

This software is provided "as is", without warranty of any kind. The author does not guarantee that the software is secure, error-free, reliable, or suitable for any specific purpose.

Use this software at your own risk. The author is not responsible for any damages, data loss, security issues, outages, misconfigurations, or other problems that may occur from using, modifying, deploying, or redistributing this software.

The web interface is intended for local network or VPN access only. It should not be exposed directly to the public internet without proper security hardening, such as HTTPS, secure reverse proxy configuration, strong authentication, and additional security review.

This project is not intended to replace professional monitoring, security, or network diagnostic tools.

---

## Project Status

This project is currently in early development.

The exact implementation details are still being planned and built step by step.

---

## Motivation

This project was started because of recurring stability issues with my current internet connection. Instead of only relying on subjective impressions, I wanted to build a small tool that can collect useful connection data over time.

The goal is to better understand when connection problems happen, how often they occur, and how long they last.

At the same time, this project is used as a practical learning project for programming, Docker, monitoring, and homelab infrastructure.

---

## Goals

The project should eventually be able to:

* Check whether the internet connection is available
* Measure connection quality, for example latency
* Detect internet outages
* Store useful monitoring data
* Generate readable output or reports
* Run inside Docker
* Be deployable with Docker Compose
* Be understandable and maintainable as a small homelab tool
* Provide a local web interface for viewing status and changing settings
* Support password-based login for the web interface
* Use browser sessions/cookies so users do not have to log in every time
* Require password setup or password change on first use

---

## Learning Goals

This project is also meant to improve practical programming and infrastructure skills.

Important learning topics include:

* Designing a small monitoring service
* Thinking in states, for example online and offline
* Handling repeated checks over time
* Logging and storing measured data
* Structuring a small software project
* Coding a website to configure settings
* Running an application inside Docker
* Using Docker Compose for deployment
* Keeping configuration separate from source code
* Writing useful documentation for a GitHub project

---

## Planned Deployment Idea

The application should be able to run as a Docker container.

The long-term goal is that someone can deploy it with Docker Compose without needing to manually install many dependencies on the host system.

The exact Docker setup will be developed as part of the project.

---

## Planned Project Direction

The project will be built in small steps:

1. Basic connection check
2. Repeated monitoring loop
3. Simple data storage
4. Outage detection logic
5. Basic Docker support
6. Docker Compose deployment
7. Simple local web interface
8. Settings page
9. First-time password setup
10. Login and session handling
11. Report or export functionality
12. Documentation and cleanup

The exact file formats, configuration structure, and output format are not finalized yet.

---

## Privacy and Security

This tool is intended to run locally in a homelab environment.

It should not require public internet access to the service itself.

Configuration files and generated monitoring data may contain personal or network-related information and should be handled carefully.

The web interface is intended for local homelab or VPN access only. It should not be exposed directly to the public internet without additional security considerations such as HTTPS, secure reverse proxy configuration, and proper authentication hardening.

---

## Repository Purpose

This repository is part of a personal learning and portfolio project.

It is meant to demonstrate practical work with:

* Programming
* Basic network monitoring
* Docker
* Linux server usage
* Homelab infrastructure
* Documentation
* Step-by-step software development

---

## License

This project is licensed under the Apache License 2.0.

You are allowed to use, modify, distribute, fork, and use this project commercially, as long as the license terms are followed.

Please keep a visible attribution to the original project repository:

https://github.com/SBergerem/InterConMon

This software is provided without warranty. The author is not responsible for damages, security issues, data loss, outages, or other problems caused by using, modifying, or deploying this software.
