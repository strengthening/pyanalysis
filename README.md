# pyanalysis

[![build](https://github.com/strengthening/pyanalysis/workflows/build/badge.svg)](https://github.com/strengthening/pyanalysis/actions)
[![release](https://github.com/strengthening/pyanalysis/workflows/release/badge.svg)](https://github.com/strengthening/pyanalysis/actions)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

A lightweight Python utility library providing MySQL connection pooling, logging handlers, email utilities, and datetime helpers.

## Features

- **MySQL Connection Pool** - Thread-safe connection pooling with configurable size, timeout, and auto-reconnect
- **Logger Handlers** - Pre-configured handlers for development and production environments
- **Mail Client** - SMTP client supporting SSL/TLS with attachments
- **Moment** - Extended Arrow datetime with timestamp utilities

## Installation

### Using pip

```bash
git clone https://github.com/strengthening/pyanalysis.git
cd pyanalysis
pip install .
```

### Using conda

Create an `environment.yml` file:

```yaml
name: myenv
channels:
  - defaults
dependencies:
  - python>=3.8
  - pip
  - pip:
      - git+https://github.com/strengthening/pyanalysis.git
```

Then run:

```bash
conda env create -f environment.yml
```

## Requirements

- Python >= 3.8
- arrow >= 1.0.0
- PyMySQL >= 1.0.0

## Quick Start

### MySQL Connection Pool

```python
from pyanalysis.mysql import Pool, Conn, Trans, add_pool

# Create and register a connection pool
pool = Pool(
    size=10,
    host='localhost',
    port=3306,
    user='root',
    password='password',
    database='mydb',
    charset='utf8mb4'
)
add_pool(pool)

# Query data
conn = Conn(pool.name)
users = conn.query("SELECT * FROM users WHERE status = ?", (1,))
user = conn.query_one("SELECT * FROM users WHERE id = ?", (123,))
conn.close()

# Stream large result sets
conn = Conn(pool.name)
for row in conn.query_range("SELECT * FROM large_table", size=1000):
    process(row)
conn.close()

# Transaction
trans = Trans(pool.name)
try:
    trans.execute("UPDATE accounts SET balance = balance - ? WHERE id = ?", (100, 1))
    trans.execute("UPDATE accounts SET balance = balance + ? WHERE id = ?", (100, 2))
    trans.commit()
except Exception:
    trans.rollback()
finally:
    trans.close()
```

### Logger Handlers

```python
import logging
from pyanalysis.logger import (
    DebugHandler,
    ReleaseRotatingFileHandler,
    ReleaseTimedRotatingFileHandler,
    AlarmSMTPHandler
)

logger = logging.getLogger(__name__)

# Development: console output (DEBUG level)
logger.addHandler(DebugHandler())

# Production: rotating file (WARNING level, 10MB per file, 10 backups)
logger.addHandler(ReleaseRotatingFileHandler('app.log'))

# Production: daily rotation (WARNING level, 10 days retention)
logger.addHandler(ReleaseTimedRotatingFileHandler('app.log'))

# Critical alerts via email
logger.addHandler(AlarmSMTPHandler(
    host='smtp.example.com',
    port=587,
    username='alert@example.com',
    password='password',
    fromaddr='alert@example.com',
    toaddrs=['admin@example.com'],
    subject='Critical Alert'
))
```

### Mail Client

```python
from pyanalysis.mail import Mail, HtmlContent, ExcelAttach, ImageAttach

mail = Mail(
    username='sender@qq.com',
    password='your_password',
    host='smtp.qq.com',
    mail_port=465,
    protocol='SSL'
)

# Add HTML content
mail.attach(HtmlContent('<h1>Hello</h1><p>This is a test email.</p>'))

# Add attachments
mail.attach(ExcelAttach('/path/to/report.xlsx', 'report.xlsx'))
mail.attach(ImageAttach('/path/to/image.png', 'image.png'))

# Send
mail.send(
    title='Monthly Report',
    receivers=['recipient@example.com'],
    copiers=['cc@example.com']
)
```

### Moment (Datetime Utilities)

```python
from pyanalysis.moment import moment

# Get current time
now = moment.now()
print(now.format('YYYY-MM-DD HH:mm:ss'))

# Timestamp conversions
print(now.second_timestamp)       # Unix timestamp (seconds)
print(now.millisecond_timestamp)  # Milliseconds (13 digits)
print(now.microsecond_timestamp)  # Microseconds

# Parse timestamps (auto-detects 13-digit millisecond timestamps)
dt = moment.get(1703980800000)  # Millisecond timestamp
dt = moment.get(1703980800)     # Second timestamp
dt = moment.get('2024-01-01')   # String
```

## Development

### Run Tests

```bash
python3 -m unittest test/mysql.py
python3 -m unittest test/logger.py
python3 -m unittest test/moment.py
python3 -m unittest test/mail.py
```

### Lint

```bash
pip install flake8
flake8 . --max-line-length=127
```

### Build

```bash
python3 setup.py sdist
pip install dist/pyanalysis-*.tar.gz
```

## Release

Create a tag with `release-v*` pattern to trigger GitHub Actions release:

```bash
git tag -a release-v2.0.3 -m "v2.0.3"
git push origin release-v2.0.3
```

## License

MIT License

## Contributing

Issues and pull requests are welcome at [GitHub](https://github.com/strengthening/pyanalysis).
