"""PydanticAI demonstration of structured prompt/response of fine grained access control.

This demo uses Permit.io for fine-grained access control and PydanticAI for secure AI interactions.
"""

import os
from dataclasses import dataclass
from typing import Any, Final, Literal, Optional, TypeVar, Union

from pydantic import BaseModel, Field

from pydantic_ai import Agent, RunContext

# Define types for Permit.io - used whether or not the real module is available
# This allows type checking to work correctly even if Permit is not installed
T = TypeVar('T')


class PermitApiError(Exception):
    """Exception raised when Permit.io API encounters an error."""

    pass


class Permit:
    """Stub class for Permit.io."""

    def __init__(self, token: str = '', pdp: str = '') -> None:
        """Initialize Permit client.

        Args:
            token: Permit API token
            pdp: Permit PDP URL
        """
        pass

    async def check(self, user: str, action: str, resource: Any) -> bool:
        """Check if user has permission to perform action on resource.

        Args:
            user: User ID
            action: Action to check
            resource: Resource to check permission against

        Returns:
            True if permitted, False otherwise
        """
        return True


# Try to import the real Permit.io library
permit_available = False
try:
    # Use import error suppression with typing.TYPE_CHECKING
    from typing import TYPE_CHECKING

    if not TYPE_CHECKING:
        from permit import Permit as RealPermit
        from permit.exceptions import PermitApiError as RealPermitApiError

        # If import succeeds, use the real classes instead of our stubs
        Permit = RealPermit
        PermitApiError = RealPermitApiError
        permit_available = True
except ImportError:
    # Use the stub classes defined above
    pass

# Permit.io configuration from environment
PERMIT_KEY: Final[str] = os.environ.get('PERMIT_KEY', 'test_key')
if not PERMIT_KEY:
    raise ValueError('PERMIT_KEY environment variable not set')
PDP_URL: Final[str] = os.environ.get('PDP_URL', 'http://localhost:7766')


class SecurityError(Exception):
    """Custom exception for security-related errors."""

    pass


class UserContext(BaseModel):
    """User context containing identity and role information for permission checks."""

    user_id: str
    tier: Literal['opted_in_user', 'restricted_user', 'premium_user'] = Field(description="User's permission tier")


class FinancialQuery(BaseModel):
    """Input model for financial queries with context for permission checks."""

    question: str
    context: UserContext


class FinancialResponse(BaseModel):
    """Output model for financial advice with compliance tracking."""

    answer: str
    includes_advice: bool = Field(default=False, description='Indicates if response contains financial advice')
    disclaimer_added: bool = Field(default=False, description='Tracks if regulatory disclaimer was added')
    metadata: Optional[dict[str, str]] = Field(default=None, description='Additional metadata about the response')


@dataclass
class PermitDeps:
    """Dependencies for Permit.io integration."""

    permit: Permit
    user_id: str

    def __post_init__(self) -> None:
        if not self.permit:
            self.permit = Permit(
                token=PERMIT_KEY,
                pdp=PDP_URL,
            )


# Initialize the financial advisor agent with security focus
financial_agent = Agent[PermitDeps, FinancialResponse](
    'anthropic:claude-3-5-sonnet-latest',
    deps_type=PermitDeps,
    result_type=FinancialResponse,
    system_prompt='You are a financial advisor. Follow these steps in order:'
    '1. ALWAYS check user permissions first'
    '2. Only proceed with advice if user has opted into AI advice'
    '3. Only attempt document access if user has required permissions',
)


def classify_prompt_for_advice(question: str) -> bool:
    """Mock classifier that checks if the prompt is requesting financial advice.

    In a real implementation, this would use more sophisticated NLP/ML techniques.

    Args:
        question: The user's query text

    Returns:
        bool: True if the prompt is seeking financial advice, False if just information
    """
    # Simple keyword-based classification
    advice_keywords: Final[list[str]] = [
        'should i',
        'recommend',
        'advice',
        'suggest',
        'help me',
        "what's best",
        'what is best',
        'better option',
    ]

    question_lower = question.lower()
    return any(keyword in question_lower for keyword in advice_keywords)


@financial_agent.tool
async def validate_financial_query(
    ctx: RunContext[PermitDeps],
    query: FinancialQuery,
) -> Union[bool, str]:
    """Validates whether users have explicitly consented to receive AI-generated financial advice.

    Ensures compliance with financial regulations regarding automated advice systems.

    Key checks:
    - User has explicitly opted in to AI financial advice
    - Consent is properly recorded and verified
    - Classifies if the prompt is requesting advice

    Args:
        ctx: Context containing Permit client and user ID
        query: The financial query to validate

    Returns:
        bool: True if user has consented to AI advice, False otherwise
    """
    try:
        # Classify if the prompt is requesting advice
        is_seeking_advice = classify_prompt_for_advice(query.question)

        if not permit_available:
            print('WARNING: Permit.io not available. Bypassing permission check for financial query validation.')
            return True

        permitted = await ctx.deps.permit.check(
            user=ctx.deps.user_id,
            action='receive',
            resource={
                'type': 'financial_advice',
                'attributes': {'is_ai_generated': is_seeking_advice},
            },
        )

        if not permitted:
            if is_seeking_advice:
                return 'User has not opted in to receive AI-generated financial advice'
            else:
                return 'User does not have permission to access this information'

        return True

    except PermitApiError as e:
        raise SecurityError(f'Permission check failed: {str(e)}')


def classify_response_for_advice(response_text: str) -> bool:
    """Mock classifier that checks if the response contains financial advice.

    In a real implementation, this would use:
    - NLP to detect advisory language patterns
    - ML models trained on financial advice datasets

    Args:
        response_text: The AI-generated response text

    Returns:
        bool: True if the response contains financial advice, False if just information
    """
    # Simple keyword-based classification
    advice_indicators: Final[list[str]] = [
        'recommend',
        'should',
        'consider',
        'advise',
        'suggest',
        'better to',
        'optimal',
        'best option',
        'strategy',
        'allocation',
    ]

    response_lower = response_text.lower()
    return any(indicator in response_lower for indicator in advice_indicators)


@financial_agent.tool
async def validate_financial_response(ctx: RunContext[PermitDeps], response: FinancialResponse) -> FinancialResponse:
    """Ensures all financial advice responses meet regulatory requirements and include necessary disclaimers.

    Key features:
    - Automated advice detection using content classification
    - Regulatory disclaimer enforcement
    - Compliance verification and auditing

    Args:
        ctx: Context containing Permit client and user ID
        response: The financial response to validate

    Returns:
        FinancialResponse: Validated and compliant response
    """
    try:
        # Classify if response contains financial advice
        contains_advice = classify_response_for_advice(response.answer)

        if not permit_available:
            print('WARNING: Permit.io not available. Adding disclaimer to all advice responses by default.')
            # When Permit isn't available, always add disclaimers for financial advice
            if contains_advice:
                disclaimer = (
                    '\n\nIMPORTANT DISCLAIMER: This is AI-generated financial advice. '
                    'This information is for educational purposes only and should not be '
                    'considered as professional financial advice. Always consult with a '
                    'qualified financial advisor before making investment decisions.'
                )
                response.answer += disclaimer
                response.disclaimer_added = True
                response.includes_advice = True
            return response

        # Check if user is allowed to receive this type of response
        permitted = await ctx.deps.permit.check(
            ctx.deps.user_id,
            'requires_disclaimer',
            {
                'type': 'financial_response',
                'attributes': {'contains_advice': str(contains_advice)},
            },
        )

        if contains_advice and permitted:
            disclaimer = (
                '\n\nIMPORTANT DISCLAIMER: This is AI-generated financial advice. '
                'This information is for educational purposes only and should not be '
                'considered as professional financial advice. Always consult with a '
                'qualified financial advisor before making investment decisions.'
            )
            response.answer += disclaimer
            response.disclaimer_added = True
            response.includes_advice = True

        return response

    except PermitApiError as e:
        raise SecurityError(f'Failed to check response content: {str(e)}')


# Example usage
async def main() -> None:
    """Run example usage of the financial advisor agent."""
    # Initialize Permit client
    if permit_available:
        permit: Permit = Permit(
            token=PERMIT_KEY,
            pdp=PDP_URL,
        )
    else:
        print('WARNING: Permit.io not available. Using stub implementation with simulated security.')
        permit = Permit()

    # Create security context for the user
    deps: PermitDeps = PermitDeps(permit=permit, user_id='user@example.com')

    try:
        # Example: Process a financial query
        result = await financial_agent.run(
            'Can you suggest some basic investment strategies for beginners?',
            deps=deps,
        )
        print(f'Secure response: {result.data}')

    except SecurityError as e:
        print(f'Security check failed: {str(e)}')


if __name__ == '__main__':
    import asyncio

    asyncio.run(main())
