# SampleStrategyPipeline Demo Application

This directory contains a demonstration application that showcases the `SampleStrategyPipeline` functionality with sample text processing.

## Files

- `demo_app.py` - Main demonstration application (requires OpenWebUI)
- `mock_demo_app.py` - Mock demonstration application (no external dependencies)
- `event_timeline_demo.py` - Event timeline analysis demo with custom JSON schema
- `event_timeline_prompt_strategy.py` - Custom prompt strategy for event timeline analysis
- `question_answer_demo.py` - Question-answer conversational AI demo with schema
- `question_answer_prompt_strategy.py` - Custom prompt strategy for conversational AI
- `run_demo.py` - Interactive runner script for all demos
- `schemas/prompts/event_timeline_prompt_schema.json` - JSON schema for event timeline analysis
- `pyproject.toml` - Project configuration and dependencies
- `README.md` - This documentation file

## Overview

The demo application demonstrates how to:

1. **Create a SampleStrategyPipeline** with all required components
2. **Configure pipeline options** for timing, validation, and retry mechanisms
3. **Process sample text** through the three-tier strategy system
4. **Display comprehensive results** including statistics and generated content
5. **Use custom prompt strategies** with JSON schemas for specialized analysis
6. **Analyze event timelines** with temporal relationships and dependencies
7. **Create conversational AI** with question-answer schemas and context

## Features Demonstrated

### Pipeline Components
- **Prompt Strategy**: `SimplePromptCreationStrategy` for generating prompts
- **Response Strategy**: `SimpleResponseCreationStrategy` for processing LLM responses
- **XML Strategy**: `SimpleXmlOutputStrategy` for generating XML output
- **LLM Client**: `OpenWebUIClient` for communicating with language models

### Event Timeline Analysis
- **Custom Prompt Strategy**: `EventTimelinePromptStrategy` with JSON schema loading
- **Schema-Based Prompts**: Dynamic prompt generation from structured event data
- **Temporal Analysis**: Critical path identification and performance insights
- **Structured Output**: Comprehensive analysis with dependencies and optimization suggestions

### Question-Answer Conversational AI
- **Custom Prompt Strategy**: `QuestionAnswerPromptStrategy` with conversational schema
- **Conversation History**: Maintains context across multiple interactions
- **System Messages**: Configurable assistant behavior and personality
- **Context Awareness**: Additional context and user preferences support

### Pipeline Options
- **Timing**: Track execution time for each stage
- **Validation**: Validate input data and responses
- **Retry Logic**: Automatic retry with exponential backoff
- **Logging**: Comprehensive logging throughout execution

### Sample Data
The application processes sample text about artificial intelligence, including:
- Text analysis task
- Sentiment and topic analysis
- Structured output format requirements

## Usage

### Prerequisites
1. Ensure you have the PromptXML Strategies package installed
2. Have an OpenWebUI instance running (for real demo only)
3. Python 3.11+ installed
4. uv package manager installed

### Running the Demo

#### Option 1: Using uv (Recommended)
```bash
# From the project root directory
cd src/test_app

# Install dependencies and run interactive demo
uv run python run_demo.py

# Or run specific demos directly
uv run python mock_demo_app.py
uv run python demo_app.py
```

#### Option 2: Using Scripts (via uv)
```bash
# From the project root directory
cd src/test_app

# Run using the defined scripts
uv run demo-runner         # Interactive runner (recommended)
uv run demo-mock           # Mock demo directly
uv run demo-real           # Real demo directly
uv run demo-event-timeline # Event timeline demo directly
uv run demo-question-answer # Question-answer demo directly
```

#### Option 3: Direct Python Execution
```bash
# Mock demo (no external dependencies)
cd src/test_app
PYTHONPATH=.. python mock_demo_app.py

# Real demo (requires OpenWebUI)
cd src/test_app
PYTHONPATH=.. python demo_app.py

# Event timeline demo (custom schema-based)
cd src/test_app
PYTHONPATH=.. python event_timeline_demo.py

# Question-answer demo (conversational AI)
cd src/test_app
PYTHONPATH=.. python question_answer_demo.py
```

### Expected Output
The application will:
1. Initialize the pipeline with all components
2. Process the sample text through all four stages
3. Display comprehensive results including:
   - Pipeline statistics (execution count, success rate, timing)
   - Generated prompt
   - LLM response
   - Structured response
   - XML output
   - Stage timings

## Configuration

### Project Configuration
The demo app uses `pyproject.toml` for configuration and dependency management:

- **Dependencies**: All required packages managed via uv
- **Scripts**: Pre-defined entry points for easy execution (`demo-mock`, `demo-real`, `demo-runner`)
- **Development Tools**: Black, MyPy, pytest configuration included
- **Python Version**: Requires Python 3.11+
- **Package Manager**: Uses uv for fast, reliable dependency management

### Demo Customization
You can modify the demo by editing:

- **Sample Data**: Change `create_sample_data()` to use different input text
- **Pipeline Options**: Modify `pipeline_options` in `create_demo_pipeline()`
- **LLM Client**: Update the OpenWebUI configuration or use a different client
- **Logging**: Adjust the logging level and format in `setup_logging()`
- **Event Schema**: Modify `schemas/prompts/event_timeline_prompt_schema.json` for different event structures
- **Prompt Strategy**: Customize `EventTimelinePromptStrategy` for different analysis types

### JSON Schema Structure
The event timeline demo uses a structured JSON schema with the following format:

```json
{
  "name": "Event Timeline Analysis",
  "description": "Schema for analyzing event timelines...",
  "event_list": [
    {
      "id": "event_001",
      "relative_time": "00:00:00",
      "action": "System initialization started"
    }
  ],
  "events": {
    "total_count": 10,
    "time_span": "00:04:00",
    "categories": {...},
    "critical_path": [...],
    "parallel_events": [...]
  }
}
```

## Example Output

```
🎯 SampleStrategyPipeline Demo Application
==================================================
2024-01-15 10:30:00 - DemoApp - INFO - 🚀 Starting SampleStrategyPipeline Demo
2024-01-15 10:30:00 - DemoApp - INFO - ============================================================
2024-01-15 10:30:00 - DemoApp - INFO - 📋 Initializing pipeline...
2024-01-15 10:30:00 - DemoApp - INFO - ✅ Pipeline initialized successfully
2024-01-15 10:30:00 - DemoApp - INFO - 📝 Input Data:
2024-01-15 10:30:00 - DemoApp - INFO -    Task: analyze_text
2024-01-15 10:30:00 - DemoApp - INFO -    Analysis Type: sentiment_and_topic
2024-01-15 10:30:00 - DemoApp - INFO -    Text Length: 1234 characters
...
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure you're running from the correct directory and the package is installed
2. **LLM Connection**: Verify your OpenWebUI instance is running and accessible
3. **Logging Issues**: Check file permissions for the log file creation

### Debug Mode

To enable more detailed logging, modify the logging level in `setup_logging()`:

```python
logging.basicConfig(level=logging.DEBUG, ...)
```

This will show detailed information about each pipeline stage and internal operations.
