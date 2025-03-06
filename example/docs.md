# Secure AI Access Control with PydanticAI

Imagine you're building an AI financial advisor. You need to ensure:

- Only authorized users receive financial advice
- Every AI response complies with regulations
- Every interaction is properly validated

This example demonstrates how to implement a secure financial advisor agent using PydanticAI's structured response system and Permit.io permission checks.

## The Challenge

In this financial agent example, we face two key challenges:

1. **Unstructured AI Responses**: Without proper structure, AI outputs can be unpredictable and difficult to validate. This is especially problematic in regulated domains like finance where you need to:

   - Verify if a response contains financial advice
   - Add required disclaimers
   - Prevent unauthorized advice

2. **Complex Permission Logic**: Traditional approaches to permission checks look like this:

```python
def check_user_access(user_id: str, request: dict) -> bool:
    # Complex dictionary parsing
    if request.get('type') == 'financial_advice':
        if request.get('opted_for_ai_advice'):
            # More nested checks...
            pass
    return False
```

Checking user permissions in this way is error-prone, hard to maintain, and lacks type-safe validation. There is a better way to address these challenges using PydanticAI.

## The PydanticAI Advantage

PydanticAI enables us to define structured types for our entire AI interaction flow, transforming this complexity into a structured, type-safe system:

With our financial agent set up using PydanticAI, we can create function tools for secure AI access control in our application. We'll create two tools: one for validating user permissions to receive AI-generated advice and another for checking if the AI model's response contains financial advice. For handling our financial agent user permissions, we leverage Permit.io to create and enforce fine-grained permissions in our AI system.

## Demo

Watch how PydanticAI ensures secure financial advice:

<a href="https://imgur.com/MFNGtDV"><img src="https://i.imgur.com/MFNGtDV.gif" title="source: imgur.com" /></a>

## Running the Example

```bash
python/uv-run -m pydantic_ai_examples.secure-ai-agent
```

## Example Implementation

Here is the complete example code for our agent:

```python {title="secure_ai_agent.py"}
#! examples/pydantic_ai_examples/secure-ai-agent.py
```

By combining PydanticAI's structured output and type safety with Permit.io permission checks, we can build AI systems that are both powerful and secure. The result is code that's easier to maintain, harder to break, and ready for production.
