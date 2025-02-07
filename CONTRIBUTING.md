# Contributing

## Development Environment Setup

1. Clone the repository:
```bash
git clone https://github.com/zero-system/ha-smart-thermostat
cd ha-smart-thermostat
```

2. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements_dev.txt
```

4. Install pre-commit hooks:
```bash
pre-commit install
```

## Development Process

1. Create a branch:
```bash
git checkout -b feature-name
```

2. Make your changes

3. Test your changes:
```bash
pytest
```

4. Check code style:
```bash
black .
flake8
```

5. Commit your changes:
```bash
git add .
git commit -m "Description of changes"
```

6. Push to GitHub:
```bash
git push origin feature-name
```

7. Create a Pull Request

## Testing

### Local Testing
1. Run all tests:
```bash
pytest
```

2. Test with Home Assistant:
   - Start the development container:
     ```bash
     docker-compose up -d
     ```
   - Open Home Assistant: http://localhost:8123
   - Check the logs:
     ```bash
     docker-compose logs -f
     ```

## Pull Request Process

1. Update documentation if needed
2. Add tests for new features
3. Ensure all tests pass
4. Update CHANGELOG.md

## Questions?

Open an issue on GitHub