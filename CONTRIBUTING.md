# Contributing to asyncgateway

Thank you for your interest in contributing to asyncgateway! This document provides guidelines for contributing to the project.

## Getting Started

### Development Environment

Please see [docs/development.md](docs/development.md) for detailed instructions on setting up your development environment.

### Quick Setup

1. Fork and clone the repository
2. Install dependencies: `uv sync --group dev`
3. Run tests to verify setup: `uv run pytest`

## How to Contribute

### Reporting Issues

- Use the GitHub issue tracker to report bugs or request features
- Include a clear description and steps to reproduce for bugs
- For feature requests, explain the use case and expected behavior

### Pull Requests

1. **Fork the repository** and create a feature branch from `devel`
2. **Make your changes** following the coding guidelines below
3. **Write or update tests** for your changes
4. **Run the full test suite** and ensure all tests pass
5. **Run code quality checks** and fix any issues
6. **Update documentation** if necessary
7. **Submit a pull request** with a clear description

### Branch Naming

Use descriptive branch names:
- `feature/add-new-service`
- `fix/connection-timeout`
- `docs/update-readme`

## Coding Guidelines

### Code Style

- Follow existing code style and conventions
- Use meaningful variable and function names
- Keep functions focused and concise
- Add docstrings for public functions and classes

### Code Quality Tools

Before submitting, run these commands:

```bash
# Format code
uv run ruff format

# Check for linting issues
uv run ruff check

# Run type checking
uv run mypy src/

# Security linting
uv run bandit -r src/

# Run all tests
uv run pytest
```

### Testing

- Write tests for new features and bug fixes
- Maintain or improve test coverage
- Use descriptive test names that explain what is being tested
- Follow the existing test patterns in the codebase

### Service Implementation

When creating new services:

1. Create a new `.py` file in `src/asyncgateway/services/`
2. Import `ServiceBase` from `asyncgateway.services`
3. Define a `Service` class inheriting from `ServiceBase`
4. Set a `name` class attribute
5. Implement async methods using `self.client` for HTTP requests
6. Use the exception classification utilities for consistent error handling

Example:
```python
from asyncgateway.services import ServiceBase

class Service(ServiceBase):
    name = "myservice"

    async def get(self, resource_id: str):
        response = await self.client.get(f"/myservice/{resource_id}")
        return response.json()
```

### Exception Handling

- Use the existing exception hierarchy in `exceptions.py`
- Use `classify_httpx_error()` for consistent httpx error classification
- Provide meaningful error messages

### Documentation

- Update docstrings for public APIs
- Update relevant documentation files
- Include examples in docstrings when helpful
- Keep the README and development guide up to date

## Commit Guidelines

### Commit Messages

Follow conventional commit format:
- `feat: add new device service endpoint`
- `fix: resolve connection timeout issue`
- `docs: update contributing guidelines`
- `test: add tests for authentication flow`
- `refactor: simplify service loading logic`

### Commit Structure

- Keep commits focused and atomic
- Include tests and documentation in the same commit when appropriate
- Avoid mixing unrelated changes

## Review Process

1. All pull requests require review before merging
2. Address reviewer feedback promptly
3. Keep your branch up to date with the target branch
4. Be responsive to questions and suggestions

## Architecture Considerations

### Service Architecture

The project uses a dynamic service loading pattern:
- Services are auto-discovered from the `services/` directory
- Each service inherits from `ServiceBase`
- Services are attached to the client instance automatically
- Use the `ipsdk` client for HTTP requests

### Error Handling

- Maintain consistent error types across the library
- Use the classification utilities for httpx errors
- Provide helpful error messages to users

## Getting Help

- Check existing issues and documentation first
- Join discussions in pull requests and issues
- Ask questions in your pull request if you need guidance

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

Thank you for contributing to asyncgateway!
