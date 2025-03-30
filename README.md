# Agentic AI

A Python framework for building AI agents that can plan and execute tasks using Anthropic's Claude models.

## Features

- Task planning using Claude Haiku
- Step execution using Claude Sonnet
- Modular tool system for extending agent capabilities
- Configurable settings via environment variables

## Setup

1. Clone the repository
2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Unix/macOS
   # or
   .\venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:

   ```bash
   pip install -e .
   ```

4. Create a `.env` file with your settings:

   ```sh
   ANTHROPIC_API_KEY=your_api_key
   ANTHROPIC_MODEL=claude-3-7-sonnet-20250219
   PLANNING_MODEL=claude-3-haiku-20240307
   ```

## Usage

```python
from agent.core.agent import Agent

# Create an agent
agent = Agent()

# Run a task
result = agent.process_task("Your task description here")
```

## Configuration

Key environment variables:

- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `ANTHROPIC_MODEL`: Main model for execution (default: claude-3-7-sonnet-20250219)
- `PLANNING_MODEL`: Model for task planning (default: claude-3-haiku-20240307)
- `MAX_TOKENS_RESPONSE`: Maximum tokens for responses (default: 4096)
- `PLANNING_TEMPERATURE`: Temperature for planning (default: 0.2)
- `EXECUTION_TEMPERATURE`: Temperature for execution (default: 0.7)
- `GOOGLE_API_KEY`: Used for Google Cloud Access
- `SEARCH_ENGINE_ID`: Used for Google Programmable Search
