# Contributing to SolarScan

Thank you for your interest in contributing to SolarScan! We welcome contributions from developers, solar engineers, and open-source enthusiasts.

## How to Contribute

### 1. Reporting Bugs
- Check existing issues before submitting a new report.
- Include OS version, Python version, steps to reproduce, and terminal logs.

### 2. Feature Requests
- Describe the proposed feature, real-world utility in PV feasibility sizing, and proposed implementation details.

### 3. Pull Requests
1. Fork the repository and create a topic branch (`git checkout -b feat/my-feature`).
2. Install dependencies: `pip install -r requirements.txt`.
3. Make your changes adhering to PEP8 guidelines.
4. Add unit tests in `tests/` covering your changes.
5. Ensure 100% of tests pass: `py -m pytest`.
6. Submit a Pull Request describing your changes and link relevant issues.

## Development Setup

```bash
git clone https://github.com/IamOumarIbrahim/SolarScan.git
cd SolarScan
pip install -e .
py -m pytest
```
