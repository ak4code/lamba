# Lamba

Lamba is a project for automated trading on the Bybit exchange using its API. It includes trading strategies, risk management, and real-time market monitoring.

---

## Features

- **Automated Trading**: Ready-to-use strategies for automated trades.
- **Risk Management**: Capital protection and risk control.
- **Market Monitoring**: Real-time tracking of market changes.

---

## Technologies

- **Programming Language**: Python 3.13
- **Task Execution**: Celery

---

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ak4code/lamba.git
   cd lamba
   ```

2. Install dependencies:
   ```bash
   poetry install --no-root
   ```

3. Usage:
   ```bash
   cp .env.example .env  #Change to your secrets
   celery -A app worker -B
   ```
   
