# Logging

## Purpose

Quasimodo uses Python's built-in logging framework to record application events, warnings, and errors. Logging is intended to aid debugging, maintenance, and auditing while avoiding the use of `print()` statements in production code.

---

## Design Goals

The logging system should:

* Record important application events.
* Provide useful diagnostic information when errors occur.
* Avoid exposing sensitive information such as passwords, session cookies, or authentication tokens.
* Be easy to search and filter.
* Remain lightweight enough to run continuously on a Raspberry Pi.

---

## Log Levels

| Level    | Usage                                                |
| -------- | ---------------------------------------------------- |
| DEBUG    | Detailed information used during development.        |
| INFO     | Normal application events.                           |
| WARNING  | Unexpected situations that do not prevent operation. |
| ERROR    | Recoverable failures.                                |
| CRITICAL | Severe failures requiring immediate attention.       |

---

## General Guidelines

Use logging instead of `print()`.

Example:

```python
logger.info("Connected to master clock.")
```

instead of:

```python
print("Connected")
```

Every module should create its own logger:

```python
import logging

logger = logging.getLogger(__name__)
```

---

## Events to Log

### Application

* Application startup
* Application shutdown
* Configuration loaded
* Service restart

### Authentication

* Successful login
* Failed login
* Logout

Passwords, session cookies, and authentication tokens should **never** be written to logs.

### Clock Communication

* Connection established
* Connection failed
* Schedule downloaded
* Schedule uploaded
* Timeout
* Invalid response
* Communication errors

### Scheduler

* Schedule created
* Schedule modified
* Schedule deleted
* Schedule published
* Schedule import/export

### System

* Backup created
* Backup restored
* Configuration changed

---

## Error Logging

Whenever an exception is caught that should be recorded, use:

```python
logger.exception("Failed to update schedule.")
```

instead of:

```python
logger.error(str(error))
```

`logger.exception()` automatically records the full traceback, making debugging significantly easier.

---

## Log Files

Current structure:

```
logs/
    quasimodo.log
```

Future versions may separate logs into:

```
logs/
    app.log
    errors.log
```

Log rotation should be enabled in production to prevent unlimited file growth.

---

## Security

The following information should never be logged:

* Passwords
* Authentication tokens
* Session cookies
* Secret keys
* Personally identifiable information (PII)

If sensitive values are required for debugging, they should be partially masked.

Example:

```
192.168.1.xxx
```

instead of

```
192.168.1.102
```

---

## Recommended Logging Style

Good:

```python
logger.info("Administrator published 'Assembly Schedule'.")
```

Bad:

```python
logger.info("Done.")
```

Messages should clearly describe:

* What happened
* Which object or subsystem was involved
* Whether the operation succeeded or failed

---

## Future Improvements

Potential enhancements include:

* Rotating log files
* Separate application and error logs
* Configurable log levels
* Log viewer within the web interface
* Downloadable log archives
* Search and filtering
* Automatic cleanup of old log files

---

## Philosophy

Logging exists to explain **what happened**, **when it happened**, and **why it happened**. A good log should allow an administrator or developer to diagnose most problems without reproducing them.

Every meaningful action should leave an informative, concise, and secure record.
