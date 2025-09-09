# PromptXML Strategies Framework

A Python framework for creating structured prompts using JSON schemas with JSON-to-XML transformation capabilities. Built using Test-Driven Development practices with a three-tier strategy architecture and comprehensive validation.

## Features

- **Three-Tier Strategy Architecture**: Separate strategies for prompt creation, response processing, and XML output
- **Triple-Schema Architecture**: Prompt schemas (input validation) + Response schemas (output structure) + XSD schemas (XML transformation)
- **Interface-Based Design**: Extensible strategy system with clear separation of concerns
- **JSON-to-XML Transformation**: Automatically convert structured LLM responses to validated XML documents
- **CLI Interface**: Command-line tools for all major operations
- **Multiple LLM Clients**: Support for OpenWebUI and Anthropic APIs
- **Comprehensive Testing**: pytest framework with >90% test coverage targets
- **Modern Python**: Built with Python 3.11+, using uv package manager and pyproject.toml

## Quick Start

### Installation

```bash
# Clone the repository
cd prompt-xml-strategies

# Install with uv
uv sync --dev

# Or install from PyPI (when published)
pip install prompt-xml-strategies
```

### Basic Usage

```bash
# List all available strategies (three-tier)
uv run python -m prompt_xml_strategies.cli list-strategies

# Execute complete three-tier pipeline
uv run python -m prompt_xml_strategies.cli execute-pipeline \
  --prompt-strategy simple \
  --response-strategy simple \
  --xml-strategy simple \
  --llm-client openwebui \
  --data data/input.json \
  --output output.xml

# Test individual strategies
uv run python -m prompt_xml_strategies.cli test-strategy \
  --strategy simple --type prompt --data data/input.json
```

## Architecture

### Core Components

- **TripleStrategyPipeline**: Orchestrates the three-tier strategy execution
- **StrategyManager**: Manages registration and discovery of all three strategy types
- **PromptCreationStrategy**: Interface for prompt generation strategies
- **ResponseCreationStrategy**: Interface for response processing strategies
- **XmlOutputStrategy**: Interface for XML transformation strategies
- **OpenWebUIClient/AnthropicClient**: LLM client implementations

### Three-Tier Strategy System

#### Prompt Strategies
- **SimplePromptCreationStrategy**: Template-based prompt generation

#### Response Strategies  
- **SimpleResponseCreationStrategy**: JSON extraction with text fallback

#### XML Output Strategies
- **SimpleXmlOutputStrategy**: Basic XML transformation with context support

### Triple-Schema Workflow

1. **Prompt Schema**: Validates input data structure
2. **Response Schema**: Defines expected LLM response format
3. **XSD Schema**: Enables XML transformation with validation
4. **End-to-End**: JSON input → Validated prompt → LLM response → Validated JSON → Valid XML

## Development

### Requirements

- Python 3.11+
- uv package manager

### Build

The project uses modern Python packaging with `pyproject.toml` and the Hatchling build backend:

```bash
# Build the package
uv build

# Build wheel only
uv build --wheel

# Build source distribution only
uv build --sdist

# Install in development mode
uv sync --dev
```

### Running

#### CLI Commands

The framework provides a comprehensive CLI interface:

```bash
# List all available strategies (three-tier)
uv run python -m prompt_xml_strategies.cli list-strategies

# Get detailed information about a strategy
uv run python -m prompt_xml_strategies.cli strategy-info \
  --strategy simple --type prompt

# Execute complete pipeline
uv run python -m prompt_xml_strategies.cli execute-pipeline \
  --prompt-strategy simple \
  --response-strategy simple \
  --xml-strategy simple \
  --llm-client openwebui \
  --data data/input.json \
  --output output.xml

# Test individual strategies
uv run python -m prompt_xml_strategies.cli test-strategy \
  --strategy simple --type prompt --data data/input.json

uv run python -m prompt_xml_strategies.cli test-strategy \
  --strategy simple --type response --data data/response.json

uv run python -m prompt_xml_strategies.cli test-strategy \
  --strategy simple --type xml --data data/structured.json

# Test LLM client connectivity
uv run python -m prompt_xml_strategies.cli test-llm-client --client openwebui
```

#### Python API

```bash
# Start Python REPL with framework available
uv run python

# Run a Python script using the framework
uv run python your_script.py
```

### Testing

The project uses pytest with comprehensive test coverage requirements. All tests are designed to run without external dependencies using mock LLM clients.

#### Running All Tests

```bash
# Run all 276 tests (recommended)
uv run python -m pytest tests/ -v --no-cov

# Run all tests with coverage report
uv run python -m pytest tests/ --cov=src

# Run all tests and fail if coverage below 90%
uv run python -m pytest tests/ --cov=src --cov-fail-under=90
```

#### Test Structure

The test suite includes comprehensive coverage of all components:

- **Core Framework Tests**: Pipeline orchestration, strategy management, validation
- **Strategy Tests**: All three tiers (prompt, response, XML output strategies)
- **LLM Client Tests**: Mock and real client implementations
- **Strategy Pipeline Tests**: Complete workflow testing including QA pipeline
- **Schema Validation Tests**: JSON and XSD schema validation
- **Error Handling Tests**: Comprehensive error scenarios

#### Basic Testing Commands

```bash
# Run all tests with verbose output
uv run python -m pytest tests/ -v

# Run tests without coverage (faster)
uv run python -m pytest tests/ -v --no-cov

# Run specific test file
uv run python -m pytest tests/unit/test_simple_strategies.py -v

# Run specific test class
uv run python -m pytest tests/unit/test_qa_strategy_pipeline.py::TestQAStrategyPipeline -v

# Run specific test method
uv run python -m pytest tests/unit/test_simple_strategies.py::TestSimplePromptCreationStrategy::test_create_prompt_basic -v
```

#### Coverage Testing

```bash
# Run tests with coverage report
uv run python -m pytest tests/ --cov=src

# Generate HTML coverage report (opens in browser)
uv run python -m pytest tests/ --cov=src --cov-report=html
open htmlcov/index.html

# Generate XML coverage report for CI/CD
uv run python -m pytest tests/ --cov=src --cov-report=xml

# Coverage with detailed line-by-line report
uv run python -m pytest tests/ --cov=src --cov-report=term-missing
```

#### Test Categories

```bash
# Run only unit tests
uv run python -m pytest tests/unit/ -v

# Run only integration tests (if any)
uv run python -m pytest tests/integration/ -v

# Run tests that don't require network access
uv run python -m pytest tests/ -m "not network" -v

# Run fast tests only (exclude slow tests)
uv run python -m pytest tests/ -m "not slow" -v
```

#### Strategy-Specific Testing

```bash
# Test all prompt strategies
uv run python -m pytest tests/unit/test_*prompt_strategy.py -v

# Test all response strategies  
uv run python -m pytest tests/unit/test_*response_strategy.py -v

# Test all XML output strategies
uv run python -m pytest tests/unit/test_*xml_output_strategy.py -v

# Test strategy pipelines
uv run python -m pytest tests/unit/test_*strategy_pipeline.py -v

# Test QA workflow specifically
uv run python -m pytest tests/unit/test_qa_*.py -v
```

#### Parallel Testing

```bash
# Run tests in parallel using pytest-xdist
uv run python -m pytest tests/ -n auto -v

# Run tests on 4 CPU cores
uv run python -m pytest tests/ -n 4 -v

# Parallel testing with coverage
uv run python -m pytest tests/ -n auto --cov=src
```

#### Demo Application Testing

```bash
# Run all demo applications
cd src/test_app
uv run demo-runner

# Run specific demos
echo "1" | uv run demo-runner  # Mock demo
echo "7" | uv run demo-runner  # QA strategy pipeline demo
echo "8" | uv run demo-runner  # All demos

# Run individual demo scripts
uv run python mock_demo.py
uv run python qa_strategy_pipeline_demo.py
```

#### Continuous Integration Testing

```bash
# Full CI test suite (what runs in CI/CD)
uv run python -m pytest tests/ -v --cov=src --cov-fail-under=90 --tb=short

# Quick smoke test (for development)
uv run python -m pytest tests/unit/test_simple_strategies.py -v

# Test specific new features
uv run python -m pytest tests/unit/test_qa_strategy_pipeline.py -v
```

#### Test Debugging

```bash
# Run tests with detailed output and stop on first failure
uv run python -m pytest tests/ -v -x --tb=long

# Run tests with pdb debugger on failure
uv run python -m pytest tests/ --pdb

# Run tests with print statements visible
uv run python -m pytest tests/ -s -v

# Run specific failing test with maximum verbosity
uv run python -m pytest tests/unit/test_specific.py::test_method -vvv --tb=long
```

### Code Quality

```bash
# Format code with Black
uv run black src/ tests/

# Check code formatting
uv run black --check src/ tests/

# Lint code with flake8
uv run flake8 src/ tests/

# Type checking with mypy
uv run mypy src/

# Run all quality checks
uv run black src/ tests/ && uv run flake8 src/ tests/ && uv run mypy src/
```

### Project Structure

```
src/prompt_xml_strategies/
├── core/                    # Core framework classes
│   ├── pipeline.py          # Three-tier pipeline orchestration
│   ├── strategy_manager.py  # Strategy registration system
│   ├── exceptions.py        # Custom exception classes
│   └── ...
├── prompt_strategies/       # Prompt creation strategies
│   ├── interface.py         # PromptCreationStrategy interface
│   ├── simple_prompt_strategy.py
│   └── __init__.py
├── response_strategies/     # Response processing strategies
│   ├── interface.py         # ResponseCreationStrategy interface  
│   ├── simple_response_strategy.py
│   └── __init__.py
├── xml_output_strategies/   # XML transformation strategies
│   ├── interface.py         # XmlOutputStrategy interface
│   ├── simple_xml_strategy.py
│   └── __init__.py
├── llm_clients/            # LLM provider implementations
│   ├── base_client.py       # BaseLLMClient interface
│   ├── openwebui_client.py  # OpenWebUI/Ollama client
│   ├── anthropic_client.py  # Anthropic Claude client
│   └── __init__.py
├── cli.py                   # Command-line interface
└── __init__.py             # Main package exports
```

## Example Usage

### Python API

```python
from prompt_xml_strategies import (
    TripleStrategyPipeline, 
    get_global_strategy_manager,
    OpenWebUIClient
)

# Get strategies
manager = get_global_strategy_manager()
prompt_strategy = manager.get_prompt_strategy("simple")
response_strategy = manager.get_response_strategy("simple")
xml_strategy = manager.get_xml_strategy("simple")

# Create LLM client
llm_client = OpenWebUIClient()

# Create pipeline
pipeline = TripleStrategyPipeline(
    prompt_strategy=prompt_strategy,
    response_strategy=response_strategy,
    xml_strategy=xml_strategy,
    llm_client=llm_client
)

# Execute complete pipeline
result = pipeline.execute(
    input_data={"question": "What is machine learning?"},
    model="llama3.2"
)

# Access results
prompt = result["prompt"]
structured_response = result["structured_response"] 
xml_output = result["xml_string"]
```

### CLI Usage

```bash
# List all strategies
uv run python -m prompt_xml_strategies.cli list-strategies

# Get strategy information
uv run python -m prompt_xml_strategies.cli strategy-info \
  --strategy simple --type prompt

# Execute pipeline with all options
uv run python -m prompt_xml_strategies.cli execute-pipeline \
  --prompt-strategy simple \
  --response-strategy simple \
  --xml-strategy simple \
  --llm-client openwebui \
  --data data/input.json \
  --output output.xml \
  --save-all
```

## Contributing

1. Follow Test-Driven Development practices
2. Ensure >90% test coverage for new code
3. Use Black for code formatting
4. Add type hints for all functions
5. Update documentation when adding new strategies

## License

MIT License - see LICENSE file for details.