# PromptXML Strategies Framework

A Python framework for creating structured prompts using JSON schemas with JSON-to-XML transformation capabilities. Built using Test-Driven Development practices with a three-tier strategy architecture and comprehensive validation.

## Features

- **Three-Tier Strategy Architecture**: Separate strategies for prompt creation, response processing, and XML output
- **Triple-Schema Architecture**: Prompt schemas (input validation) + Response schemas (output structure) + XSD schemas (XML transformation)
- **Interface-Based Design**: Extensible strategy system with clear separation of concerns
- **JSON-to-XML Transformation**: Automatically convert structured LLM responses to validated XML documents
- **CLI Interface**: Command-line tools for all major operations
- **Multiple LLM Clients**: Support for OpenWebUI, OLLAMA, and Anthropic APIs
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

# Execute complete three-tier pipeline with OpenWebUI
uv run python -m prompt_xml_strategies.cli execute-pipeline \
  --prompt-strategy simple \
  --response-strategy simple \
  --xml-strategy simple \
  --llm-client openwebui \
  --data data/input.json \
  --output output.xml

# Execute pipeline with OLLAMA
uv run python -m prompt_xml_strategies.cli execute-pipeline \
  --prompt-strategy simple \
  --response-strategy simple \
  --xml-strategy simple \
  --llm-client ollama \
  --model llama3.2 \
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
- **OpenWebUIClient/OllamaClient/AnthropicClient**: LLM client implementations

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

# Test OLLAMA client connectivity
uv run python -m prompt_xml_strategies.cli test-llm-client --client ollama

# Test OLLAMA client with custom server
uv run python -m prompt_xml_strategies.cli test-llm-client \
  --client ollama \
  --base-url http://your-ollama-server:11434
```

#### Python API

```bash
# Start Python REPL with framework available
uv run python

# Run a Python script using the framework
uv run python your_script.py
```

### Testing

The project uses pytest with comprehensive test coverage requirements:

#### Basic Testing

```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/unit/test_simple_strategies.py

# Run specific test method
uv run pytest tests/unit/test_simple_strategies.py::TestSimplePromptCreationStrategy::test_create_prompt_basic
```

#### Coverage Testing

```bash
# Run tests with coverage report
uv run pytest --cov=src

# Generate HTML coverage report
uv run pytest --cov=src --cov-report=html

# Generate XML coverage report  
uv run pytest --cov=src --cov-report=xml

# Fail if coverage below 90% (as configured in pyproject.toml)
uv run pytest --cov=src --cov-fail-under=90
```

#### Test Categories

Use pytest markers to run specific test categories:

```bash
# Run only unit tests
uv run pytest -m unit

# Run only integration tests  
uv run pytest -m integration

# Run tests that don't require network access
uv run pytest -m "not network"

# Run fast tests only (exclude slow tests)
uv run pytest -m "not slow"
```

#### Parallel Testing

```bash
# Run tests in parallel using pytest-xdist
uv run pytest -n auto

# Run tests on 4 CPU cores
uv run pytest -n 4
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
│   ├── ollama_client.py     # Direct OLLAMA API client
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
    OpenWebUIClient,
    OllamaClient
)

# Get strategies
manager = get_global_strategy_manager()
prompt_strategy = manager.get_prompt_strategy("simple")
response_strategy = manager.get_response_strategy("simple")
xml_strategy = manager.get_xml_strategy("simple")

# Create LLM client (OpenWebUI)
llm_client = OpenWebUIClient()

# Or use direct OLLAMA client
# llm_client = OllamaClient()

# Or use custom OLLAMA server
# llm_client = OllamaClient(base_url="http://your-server:11434")

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

## OLLAMA Integration

The framework provides comprehensive OLLAMA integration for local LLM deployment. The `OllamaClient` offers direct access to OLLAMA API with rich features.

### Setup OLLAMA Server

```bash
# Install OLLAMA (macOS/Linux)
curl -fsSL https://ollama.ai/install.sh | sh

# Start OLLAMA server
ollama serve

# Pull models (in another terminal)
ollama pull llama3.2
ollama pull codellama:13b
ollama pull mistral
```

### OLLAMA Client Features

- **Text Generation**: Single-shot and streaming responses
- **Chat Interface**: Conversational interactions with message history
- **Model Management**: Pull, delete, copy, and inspect models
- **Embeddings**: Generate text embeddings
- **Advanced Parameters**: Full control over generation (temperature, top_p, seed, etc.)
- **Remote Servers**: Connect to any OLLAMA server via base URL

### Usage Examples

#### CLI with OLLAMA

```bash
# Execute pipeline with local OLLAMA
uv run python -m prompt_xml_strategies.cli execute-pipeline \
  --llm-client ollama \
  --model llama3.2 \
  --data data/input.json \
  --output output.xml

# Connect to remote OLLAMA server
uv run python -m prompt_xml_strategies.cli execute-pipeline \
  --llm-client ollama \
  --base-url http://192.168.1.100:11434 \
  --model codellama:13b \
  --data data/code_task.json \
  --output results.xml

# Test OLLAMA connectivity and list models
uv run python -m prompt_xml_strategies.cli test-llm-client --client ollama
```

#### Python API with OLLAMA

```python
from prompt_xml_strategies import OllamaClient, TripleStrategyPipeline

# Create OLLAMA client
ollama_client = OllamaClient()

# Or connect to remote server
# ollama_client = OllamaClient(base_url="http://your-server:11434")

# Use in pipeline
pipeline = TripleStrategyPipeline(
    prompt_strategy=prompt_strategy,
    response_strategy=response_strategy,
    xml_strategy=xml_strategy,
    llm_client=ollama_client
)

# Execute with specific model
result = pipeline.execute(
    input_data={"task": "Generate a report"},
    model="llama3.2"
)
```

### Model Management

The OLLAMA client provides extensive model management capabilities:

```python
# List available models
models = ollama_client.get_available_models()

# Get model information
info = ollama_client.get_model_info("llama3.2")

# Pull a new model
ollama_client.pull_model("mistral:7b")

# Generate embeddings
embeddings = ollama_client.embeddings("Text to embed", model="nomic-embed-text")
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
