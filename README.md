# Task Automation Monitor

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A robust task scheduling and monitoring system with automatic execution tracking and timezone-aware scheduling.

## Features

- 🕒 Automatic daily task execution tracking
- 🌍 Timezone-aware scheduling (supports Asia/Taipei by default)
- 📝 JSON configuration management
- 📊 Detailed execution logging
- 🔄 Automatic working directory management
- ⏰ 30-minute interval health checks

## Installation

1. Clone repo:
```bash
git clone https://github.com/yourusername/task-automation-monitor.git
```



## Configuration
Create config_local.py (override) or config.py:

```
tasks = {
    "database_backup": "/path/to/backup_script.py",
    "data_cleanup": "/path/to/cleanup_job.py"
}
```

Configure tasks in tasks_config.json:

```
{
    "database_backup": {
        "script_path": "/path/to/backup_script.py",
        "last_run": null
    }
}
```
Start the monitor

```
python main.py
```

## Add new task programmatically
from task_monitor import TaskMonitor
monitor = TaskMonitor()
monitor.add_task("new_task", "/path/to/script.py")


## Logging
Find execution logs in task_monitor.log with timestamps in UTC+8 format.

## Project Structure
```
TaskAutomator/
├── .gitignore          # Git exclusion rules
├── TaskAutomator.py    # Main program logic (Task monitoring core)
├── config.py           # Default task configuration
├── config_local.py     # Local override configuration (Higher priority, git-ignored)
├── tasks_config.json   # Auto-generated task execution records
├── task_monitor.log    # Runtime log file
└── README.md           # Project documentation
```
