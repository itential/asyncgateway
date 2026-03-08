# Development Environment Setup

This guide will help you set up a development environment for the asyncgateway project.

## Prerequisites

- Python 3.8 or higher
- Git
- [uv](https://github.com/astral-sh/uv) package manager

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd asyncgateway
   ```

2. **Install uv (if not already installed):**
   ```bash
   # On macOS and Linux
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # On Windows
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Set up the development environment:**
   ```bash
   # Install all dependencies and sync the virtual environment
   uv sync

   # Install development dependencies
   uv sync --group dev
   ```

## Development Workflow

### Package Management
- **Add a dependency:** `uv add <package>`
- **Remove a dependency:** `uv remove <package>`
- **Sync dependencies:** `uv sync`

### Running Tests
- **Run all tests:** `uv run pytest`
- **Run tests with verbose output:** `uv run pytest -v`
- **Run tests with coverage:** `uv run pytest --cov`
- **Run specific test pattern:** `uv run pytest -k <pattern>`
- **Run tests in specific directory:** `uv run pytest tests/`

### Code Quality
- **Check code style:** `uv run ruff check`
- **Format code:** `uv run ruff format`
- **Run type checking:** `uv run mypy src/`
- **Security linting:** `uv run bandit -r src/`

### Building the Package
- **Build distributions:** `uv build`
- **Alternative build:** `python -m build`

### Running Examples
- **Run example scripts:**
  ```bash
  uv run python examples/get.py
  uv run python examples/add_devices.py
  ```

## Project Structure

```
asyncgateway/
├── src/asyncgateway/
│   ├── client.py           # Main async client class
│   ├── services/           # Service modules (devices, etc.)
│   ├── exceptions.py       # Exception hierarchy
│   └── logger.py          # Logging configuration
├── tests/                 # Test files
├── examples/              # Example scripts
├── docs/                  # Documentation
└── pyproject.toml         # Project configuration
```

## Development Notes

- The project uses a dynamic service loading pattern where services are discovered from the `services/` directory
- Each service module must have a `Service` class inheriting from `ServiceBase`
- Services are automatically attached to the client instance
- The project uses `ipsdk` for Itential Gateway communication and `httpx` for HTTP requests

## Contributing

1. Make your changes following the existing code style
2. Run the code quality tools before committing:
   ```bash
   uv run ruff format
   uv run ruff check
   uv run mypy src/
   uv run pytest
   ```
3. Ensure all tests pass and coverage remains high
4. Follow the existing exception handling patterns using the classification utilities

## Troubleshooting

- If you encounter import errors, ensure all dependencies are installed with `uv sync`
- For test failures, run with `-v` flag for more detailed output
- Check the `CLAUDE.md` file for additional development guidance and known issues
