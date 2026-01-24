# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

pyanalysis is a Python utility library providing:
- MySQL connection pooling (`pyanalysis.mysql`)
- Logging handlers (`pyanalysis.logger`)
- Email utilities (`pyanalysis.mail`)
- Date/time utilities based on arrow (`pyanalysis.moment`)

## Commands

### Run tests
```bash
python3 -m unittest test/logger.py
python3 -m unittest test/moment.py
python3 -m unittest test/mysql.py
python3 -m unittest test/mail.py
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Build and install locally
```bash
pip install build
python -m build
pip install dist/pyanalysis-*.whl
```

### Lint
```bash
flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
```

## Architecture

### MySQL Module (`pyanalysis/mysql.py`)
- `Pool`: Connection pool with configurable size (3-100 connections), timeout, and retry logic
- `Conn`: High-level database operations (`query`, `query_one`, `query_range`, `execute`, `insert`)
- `Trans`: Transaction wrapper extending `Conn` with `commit`/`rollback` control
- `_Connection`: Internal wrapper around `pymysql.Connection` with pool-aware lifecycle
- SQL uses `?` placeholders (converted to `%s` internally)
- Global pool registry via `add_pool()`/`get_pool()`

### Logger Module (`pyanalysis/logger.py`)
- `DebugHandler`: StreamHandler for development (DEBUG level)
- `ReleaseRotatingFileHandler`: Size-based rotation (10MB, 10 backups, WARNING level)
- `ReleaseTimedRotatingFileHandler`: Daily rotation (10 backups, WARNING level)
- `AlarmSMTPHandler`: Email alerts for CRITICAL level

### Mail Module (`pyanalysis/mail.py`)
- `Mail`: SMTP client supporting SSL/TLS with attachments
- `HtmlContent`, `ExcelAttach`, `ImageAttach`: Attachment helpers

### Moment Module (`pyanalysis/moment.py`)
- `Moment`: Extends `arrow.Arrow` with `second_timestamp`, `millisecond_timestamp`, `microsecond_timestamp` properties
- `MomentFactory`: Handles 13-digit millisecond timestamps automatically
- Use via `moment.now()`, `moment.get()`, etc.

## Release Process

Tag with `v*` pattern to trigger GitHub Actions release:
```bash
git tag -a v2.0.3 -m "v2.0.3"
git push origin v2.0.3
```
