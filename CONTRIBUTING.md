# Contributing to ARC-89 Playground

Thank you for your interest in contributing! This guide will help you get started.

## Development Setup

### Prerequisites
- Python 3.13+
- Poetry for dependency management

### Installation

1. Clone the repository:
```bash
git clone git@github.com:sofinico/arc89-playgorund.git
cd arc89-playground
```

2. Install dependencies with Poetry:
```bash
poetry install
```

3. Install pre-commit hooks:
```bash
poetry run pre-commit install
poetry run pre-commit install --hook-type commit-msg
```

4. Copy environment configuration:
```bash
cp .env.example .env
# Edit .env with your configuration
```

## Development Workflow

### Running Examples

Activate the Poetry shell:
```bash
poetry shell
```

Run any example:
```bash
python examples/01_basic_metadata.py
```

### Code Quality

We use automated tools to maintain code quality:

- **Ruff**: Linting and formatting
- **mypy**: Type checking (optional)
- **pre-commit**: Automated checks before commits

Run checks manually:
```bash
poetry run ruff check .
poetry run ruff format .
poetry run mypy .
```

### Commit Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/) specification.

**Format:**
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

**Examples:**
```bash
feat(examples): add immutable metadata example
fix(setup): handle missing environment variables
docs(readme): clarify ARC-89 vs ARC-90 compliance
```

The pre-commit hook will validate your commit message format automatically.

### Pull Request Process

1. Create a feature branch: `git checkout -b feat/your-feature`
2. Make your changes
3. Ensure all tests pass and code is formatted
4. Commit with conventional commit format
5. Push and create a pull request

## Questions?

Open an issue or reach out to the maintainers.
