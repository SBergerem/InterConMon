# InterConMon – Homelab Internet Monitor

InterConMon is a Docker-based learning project for monitoring internet connection stability in a homelab environment.

The goal of this project is to build a small service that can regularly check the internet connection, detect possible outages, and store useful information about connection quality.

This project is intentionally developed step by step as a learning project. The focus is not only on building a working tool, but also on understanding the logic, structure, and deployment of a small monitoring service.

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

---

## Learning Goals

This project is also meant to improve practical programming and infrastructure skills.

Important learning topics include:

* Designing a small monitoring service
* Thinking in states, for example online and offline
* Handling repeated checks over time
* Logging and storing measured data
* Structuring a small software project
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
5. Docker support
6. Docker Compose deployment
7. Report or export functionality
8. Documentation and cleanup

The exact file formats, configuration structure, and output format are not finalized yet.

---

## Privacy and Security

This tool is intended to run locally in a homelab environment.

It should not require public internet access to the service itself.

Configuration files and generated monitoring data may contain personal or network-related information and should be handled carefully.

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

A license will be added later.
