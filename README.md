# AI Access Control example with PydanticAI and Permit

A demonstration of implementing secure AI agents using PydanticAI and Permit.io's fine-grained authorization framework. This project showcases a production-ready financial advisor AI system with comprehensive access control and compliance enforcement.

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- [Permit.io Account](https://app.permit.io) (free tier available)
- uv for dependency management

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/Permit-PydanticAI.git
cd Permit-PydanticAI
```

2. Set up your Python environment:

```bash
uv sync --all-extras
```

## 🏗️ Architecture

The project implements a four-perimeter security model for AI systems:

1. **Prompt Filtering**: Validates user permissions and query intent
2. **Data Protection**: Controls access to sensitive financial data
3. **Secure External Access**: Manages API and system interactions
4. **Response Enforcement**: Ensures compliance in AI responses

### Key Components

- `main.py`: Core application logic and AI agent implementation
- `config.py`: Permit.io configuration and ABAC setup
- `docs.md`: Comprehensive documentation and examples

## 🛠️ Development

### Setting up the Development Environment

2. Set up pre-commit hooks:

```bash
pre-commit install
```

### Code Quality

```bash
make lint  # Run linting
make format  # Format code
make typecheck # check types
```

## 📚 Documentation

Detailed documentation is available in the `example/docs.md` file, covering:

- Complete implementation guide
- Security model details
- Usage examples

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
