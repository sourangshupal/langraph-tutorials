# LangGraph Tutorial Series

A comprehensive, hands-on tutorial series teaching **LangGraph 1.1.9** from beginner to advanced level. This series is designed for Python developers who are new to AI agents and agentic frameworks.

## Overview

LangGraph is a powerful framework for building stateful, multi-actor applications with LLMs. This tutorial series will take you from basic graph construction to building production-ready, multi-agent systems.

## What You'll Learn

By completing this series, you will be able to:

- Build stateful workflows with LangGraph's StateGraph API
- Integrate OpenAI models with tool/function calling
- Implement conversation memory and persistence
- Create human-in-the-loop approval workflows
- Design multi-agent systems with parallel execution
- Apply production-ready patterns and optimizations
- Deploy LangGraph applications with confidence

## Tutorial Structure

The series consists of 13 progressive notebooks:

| Notebook | Title | Complexity | Time |
|----------|-------|------------|------|
| 01 | [Introduction to LangGraph](01_introduction_to_langgraph.ipynb) | Beginner | 90-120 min |
| 02 | [Dynamic Routing with Conditional Edges](02_conditional_routing.ipynb) | Beginner-Intermediate | 90-120 min |
| 03 | [Tool Integration and OpenAI Function Calling](03_tool_integration_openai.ipynb) | Intermediate | 120-150 min |
| 04 | [State Persistence and Memory](04_state_persistence_and_memory.ipynb) | Intermediate | 150-180 min |
| 05 | [Human-in-the-Loop and Streaming](05_human_in_the_loop_streaming.ipynb) | Advanced | 150-180 min |
| 06 | [Parallel Execution and Subgraphs](06_parallel_execution_subgraphs.ipynb) | Advanced | 180-240 min |
| 07 | [Production Patterns](07_production_patterns_advanced_features.ipynb) | Expert | 240-300 min |
| 08 | [Command Primitive, Functional API & Long-Term Memory](08_command_functional_api_longterm_memory.ipynb) | Expert | 60-75 min |
| 09 | [Multi-Agent Systems](09_multi_agent_systems.ipynb) | Expert | 60-75 min |
| 10 | [Testing, Observability & LangGraph Platform](10_testing_observability_platform.ipynb) | Expert | 45-60 min |
| 11 | [Observability & Evaluation with Langfuse](11_observability_with_langfuse.ipynb) | Expert | 30-40 min |
| 12 | [Model Context Protocol (MCP)](12_mcp_model_context_protocol.ipynb) | Expert | 45-55 min |
| 13 | [Agent2Agent Protocol (A2A)](13_a2a_agent2agent_protocol.ipynb) | Expert | 45-55 min |

## Notebook Overview

| Notebook | Topic | Level | Time |
|---|---|---|---|
| 01 | Introduction to LangGraph | Beginner | 30-40 min |
| 02 | Conditional Routing | Beginner-Int | 30-40 min |
| 03 | Tool Integration & Agents | Intermediate | 45-60 min |
| 04 | State Persistence & Memory | Intermediate | 45-60 min |
| 05 | Human-in-the-Loop & Streaming | Advanced | 50-65 min |
| 06 | Parallel Execution & Subgraphs | Advanced | 50-65 min |
| 07 | Production Patterns | Advanced | 50-65 min |
| 08 | Command Primitive, Functional API & Long-Term Memory | Expert | 60-75 min |
| 09 | Multi-Agent Systems | Expert | 60-75 min |
| 10 | Testing, Observability & LangGraph Platform | Expert | 45-60 min |

## Prerequisites

### Required
- **Python 3.12+** installed
- **uv** package manager ([install instructions](https://github.com/astral-sh/uv))
- Basic to intermediate Python programming skills
- Understanding of basic programming concepts (functions, classes, dictionaries)
- Familiarity with Jupyter Notebooks

### Helpful (but not required)
- Basic understanding of Large Language Models (LLMs)
- Experience with APIs
- Familiarity with async programming in Python

## Setup Instructions

### 1. Clone or Download

Download this repository to your local machine.

### 2. Install Dependencies

```bash
# Prerequisites: Python 3.12+, uv (https://github.com/astral-sh/uv)

# 1. Create virtual environment
uv venv --python 3.12
source .venv/bin/activate  # macOS/Linux
# .venv\Scripts\activate   # Windows

# 2. Install all dependencies
uv pip install -e .

# 3. Configure API key
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 4. Start Jupyter
jupyter notebook
```

This will open Jupyter in your browser. Navigate to the first notebook to get started!

### 3. Get OpenAI API Key

1. Sign up or log in at [OpenAI Platform](https://platform.openai.com/)
2. Navigate to [API Keys](https://platform.openai.com/api-keys)
3. Create a new API key
4. Copy the API key (you won't be able to see it again!)

### 4. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API keys
# OPENAI_API_KEY=sk-your-actual-key-here
```

## Cost Considerations

These tutorials use OpenAI's API, which is a paid service. Here's what to expect:

- **Most exercises**: Use GPT-3.5-turbo (very affordable, ~$0.002 per request)
- **Advanced examples**: Use GPT-4-turbo (more expensive, ~$0.01-0.03 per request)
- **Total estimated cost**: $2-5 to complete all notebooks

Tips to minimize costs:
- Start with GPT-3.5-turbo for practice
- Set usage limits in your OpenAI account
- Use smaller input/output token limits during testing

## Learning Path

### For Complete Beginners
Start with Notebook 01 and work through sequentially. Don't skip notebooks, as each builds on previous concepts.

### For Developers with LLM Experience
You can skim Notebooks 01-02 and start deeper engagement from Notebook 03 onwards.

### For Experienced AI Developers
Review Notebooks 01-04 quickly, then focus on Notebooks 05-07 for advanced patterns.

## Projects Included

- **Notebook 04**: Customer Support Bot with persistent memory
- **Notebook 05**: Research Assistant with human-in-the-loop
- **Notebook 06**: Multi-Agent Research System with parallel processing
- **Notebook 07**: Enterprise Customer Support System (capstone project)

## Troubleshooting

### Import Errors

If you encounter import errors:

```bash
# Ensure you're in the virtual environment
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

# Reinstall dependencies
uv pip install -e .
```

### API Key Issues

If you get authentication errors:

1. Check that your `.env` file exists and contains your API key
2. Ensure there are no quotes around the API key in `.env`
3. Restart your Jupyter kernel after changing `.env`

### Version Compatibility

If you encounter compatibility issues:

```bash
# Check Python version
python --version  # Should be 3.12.x or later

# Check LangGraph version
uv pip show langgraph  # Should be 1.1.9 or later
```

## Additional Resources

- [LangGraph Official Documentation](https://langchain-ai.github.io/langgraph/)
- [LangGraph Python API Reference](https://langchain-ai.github.io/langgraph/reference/graphs/)
- [LangChain Documentation](https://python.langchain.com/)
- [OpenAI API Documentation](https://platform.openai.com/docs)

## Support

If you encounter issues or have questions:

1. Check the troubleshooting section above
2. Review the [LangGraph documentation](https://langchain-ai.github.io/langgraph/)
3. Search for similar issues on [LangGraph GitHub](https://github.com/langchain-ai/langgraph/issues)

## License

This tutorial series is provided for educational purposes.

## Version History

- **v2.0** (April 2026) - Major update
  - Expanded to 10 comprehensive notebooks
  - Compatible with LangGraph 1.1.9
  - Migrated to uv + pyproject.toml for package management
  - Added Notebooks 08-10: Multi-Agent Systems, Long-Term Memory, Testing & Observability
  - LangGraph Platform deployment coverage

- **v1.0** (December 2025) - Initial release
  - 7 comprehensive notebooks
  - Compatible with LangGraph 1.0.5
  - Python 3.12/3.13 support
  - Latest LangGraph features (caching, deferred nodes, hooks)

---

**Ready to start?** Open [Notebook 01: Introduction to LangGraph](01_introduction_to_langgraph.ipynb) and begin your journey into agentic AI!
