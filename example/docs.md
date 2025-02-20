# Fine-Grained Permissions for AI Agents

This example demonstrates how to implement a secure financial advisor agent using PydanticAI with four distinct access control perimeters. The implementation showcases a production-ready AI system that enforces certification requirements, regulatory compliance, and proper risk management.

## Key Features

This example demonstrates:

- Dynamic system prompts with proper access controls
- Structured result validation using type hints
- Comprehensive result validation through validator functions
- Secure tool implementation and management

## Access Control Perimeters Overview

The implementation follows a four-perimeter security model:

### 1. Prompt Filtering

The first perimeter validates user permissions before queries reach the AI model. This ensures users can only make requests within their authorized scope and have explicitly opted in for AI-generated financial advice.

Key functionality:

- User opt-in verification for AI-generated advice
- Query intent classification for permission mapping

```python
@financial_agent.tool
async def validate_financial_query(
    ctx: RunContext[PermitDeps],
    query: FinancialQuery,
) -> Dict[str, bool]:
```

### 2. Data Protection

The second perimeter manages access to knowledge sources and reference data. This layer ensures the AI model only accesses authorized information based on data classification levels and user permissions.

Key functionality:

- Controlled access to sensitive financial knowledge bases
- User clearance level verification for document access

```python
@financial_agent.tool
async def access_financial_knowledge(
    ctx: RunContext[PermitDeps],
    query: FinancialQuery
) -> List[str]:
```

### 3. Secure External Access

The third perimeter governs interactions with external systems and APIs. This layer maintains proper security boundaries by enforcing authentication and authorization for all external operations.

Key functionality:

- Portfolio operation authorization checks
- External API access control management

```python
@financial_agent.tool
async def check_action_permissions(
    ctx: RunContext[PermitDeps],
    action: str,
    context: UserContext
) -> bool:
```

### 4. Response Enforcement

The final perimeter validates AI-generated responses before delivery to users. This critical layer ensures all responses meet compliance requirements and include necessary disclaimers while preventing sensitive information leakage.

Key functionality:

- Financial regulation compliance verification
- Risk disclosure and disclaimer management
- Unauthorized advice distribution prevention

```python
@financial_agent.tool
async def validate_financial_response(
    ctx: RunContext[PermitDeps],
    response: FinancialResponse,
    context: UserContext
) -> Dict[str, bool]:
```

## Implementation Guide

### Environment Configuration

First, configure your Permit.io environment by obtaining a [free API key](https://app.permit.io) and setting the required environment variables:

```bash
# Required environment variables
export PERMIT_KEY='your-api-key'  # Your Permit.io API key
export PDP_URL='http://localhost:7766'  # Your PDP URL (default: http://localhost:7766)
```

The application automatically loads these environment variables:

```python
from dotenv import load_dotenv
import os

# Load environment variables from .env file if present
load_dotenv()

# Get Permit.io configuration from environment
PERMIT_KEY = os.environ["PERMIT_KEY"]
PDP_URL = os.environ.get("PDP_URL", "http://localhost:7766")

# Initialize Permit client with environment configuration
permit = Permit(
    token=PERMIT_KEY,
    pdp=PDP_URL,
)
```

### Setup Process

1. Initialize the required resources and roles in Permit.io by running the configuration script:

```bash
python/uv-run -m pydantic_ai_examples.secure-ai-config
```

The configuration establishes a comprehensive ABAC (Attribute-Based Access Control) model with the following components:

#### Resources and Attributes

- `financial_advice`: AI-generated advice with risk levels
- `financial_document`: Documents with classification levels and clearance requirements
- `financial_response`: Response content with advice detection
- `portfolio`: Investment portfolios with value tiers

#### Access Control Components

- **Condition Sets**

  - Document Clearance Check: Validates user's clearance level
  - AI Advice Opt-in Check: Verifies user consent

- **User Sets**

  - Opted-in Users: Users who have consented to AI advice
  - High Clearance Users: Users with elevated access privileges

- **Resource Sets**

  - Confidential Documents: High-security financial documents
  - AI Finance Advice: Financial advice with AI capabilities

- **Roles and Permissions**
  - Resources: financial_advice, financial_document, financial_response, portfolio
  - Roles: restricted_user, premium_user
  - Permissions: Granular access levels for each role

## Permission Structure

The following diagram illustrates our ABAC policy implementation in Permit.io, showing granular permissions for different user roles:

![permit policy](https://hackmd.io/_uploads/ryOKcyxqJx.png)

## Demo

Watch a demonstration of the Financial Advisor AI Agent in action:

<a href="https://imgur.com/MFNGtDV"><img src="https://i.imgur.com/MFNGtDV.gif" title="source: imgur.com" /></a>

## Running the Example

After installing dependencies and configuring environment variables, follow these steps:

1. Set up the Permit.io configuration:

```bash
python/uv-run -m pydantic_ai_examples.secure-ai-config
```

2. Launch the application:

```bash
python/uv-run -m pydantic_ai_examples.secure-ai-agent
```

## Example Implementation

The implementation consists of two main components:

1. Application Logic:

```python {title="secure_ai_agent.py"}
#! examples/pydantic_ai_examples/secure-ai-agent.py
```

2. Permission Configuration:

```python {title="secure-ai-config.py"}
#! examples/pydantic_ai_examples/secure-ai-config.py
```

## Additional Resources

To deepen your understanding of the concepts used in this implementation, explore these resources:

1. [Understanding Fine-Grained Authorization (FGA)](https://www.permit.io/blog/what-is-fine-grained-authorization-fga) - Learn about FGA fundamentals and its advantages over traditional access control methods.

2. [Implementing ABAC Authorization](https://www.permit.io/blog/how-to-implement-abac) - A comprehensive guide to designing and implementing ABAC systems.

3. [RBAC vs ABAC: Authorization Model Comparison](https://www.permit.io/blog/rbac-vs-abac) - Understanding how RBAC and ABAC complement each other in modern authorization systems.
