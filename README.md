# Maritime Event Detection Near Protected Waters

![](./maritime_event.gif)

## Overview

This project simulates maritime detection and response activity on a live map. Vessels are tracked as they move through their environment. When a vessel enters a protected area of interest (AOI), the system triggers an alert and sends interceptors from the nearest coastal installations to converge with the intruder. The app also records events and produces a report from the generated logs.

This version is intentionally simplified. Think of it like your starter template.

## Current Features

* Live vessel tracking with coordinate and updates
* Restricted-zone monitoring and breach detection
* Automated alerting when an intruder enters the AOI
* Response dispatch from nearby coastal installations
* Interceptor convergence behavior
* Event table with timestamps and interpretations
* Playback delay control for simulation speed
* Map-based visualization of vessel movement and response activity
* Report generation from simulation logs

## Why this exists

This app is part of a broader body of work around situational intelligence: building systems that combine event detection, reasoning, and contextual interpretation across modalities.

## Beta Notes

This is a demo.

* The current build is a trimmed-down template
* The app is best treated as a foundation for experimentation and extension
* Expect rough edges

## Project Goals

* Explore event detection in a maritime context
* Visualize response workflows in a clear and interactive way
* Create reusable simulation patterns for future situational-intelligence apps
* Provide a base template that others can modify for their own use cases

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/YOUR-USERNAME/YOUR-REPO-NAME.git
cd YOUR-REPO-NAME
```

### 2. Create or activate a virtual environment

**macOS & Linux**

```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows (PowerShell)**

```bash
python -m venv venv
venv\Scripts\Activate.ps1
```

> You should see your shell prefixed with `(venv)` once activated.

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the app

```bash
python app.py
```

## Roadmap

Potential next steps for the project:

* Reintroduce dynamic scenario generation in a cleaner architecture
* Add richer logging and export options
* Expand response logic and asset behavior
* Support additional detection inputs and event types
* Improve UI polish and controls
* Add test coverage and deployment instructions

## Sharing / Feedback

If this kind of simulation, event detection, or situational-intelligence tooling is interesting to you, feedback is welcome.

## License

GNU GPLv3
