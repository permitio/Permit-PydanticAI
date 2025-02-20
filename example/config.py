"""Permit.io configuration for Financial Advisor security perimeters.

Sets up the complete ABAC (Attribute-Based Access Control) model including:
- Resources and their attributes
- Roles and their base permissions
- Condition sets for fine-grained access control
- User sets with their attributes
- Resource sets based on classification levels
"""

import asyncio
import os
from typing import NotRequired, TypedDict

from dotenv import load_dotenv
from permit import ConditionSetCreate, Permit, ResourceAttributeCreate, ResourceCreate, RoleCreate

load_dotenv()

# API keys
PERMIT_KEY = os.environ['PERMIT_KEY']

# Initialize Permit.io SDK
permit = Permit(
    token=PERMIT_KEY,
)


# Define resources for Financial Advisor security
class ActionConfig(TypedDict):
    """Type definition for action configuration."""

    pass  # Empty dict for actions


class AttributeConfig(TypedDict):
    """Type definition for attribute configuration."""

    type: str
    description: str


class ResourceConfig(TypedDict):
    """Type definition for resource configuration."""

    key: str
    name: str
    description: str
    actions: dict[str, ActionConfig]
    attributes: dict[str, AttributeConfig]


class PermissionConfig(TypedDict):
    """Type definition for permission configuration."""

    resource: str
    actions: list[str]


class RoleConfig(TypedDict):
    """Type definition for role configuration."""

    name: str
    permissions: NotRequired[list[PermissionConfig]]


resources: list[ResourceConfig] = [
    {
        'key': 'financial_advice',
        'name': 'Financial Advice',
        'description': 'AI-generated financial advice',
        'actions': {
            'receive': {},
        },
        'attributes': {
            'is_ai_generated': {
                'type': 'bool',
                'description': 'Whether the advice is AI-generated',
            },
            'risk_level': {
                'type': 'string',
                'description': 'Risk level of the advice (low, medium, high)',
            },
        },
    },
    {
        'key': 'financial_document',
        'name': 'Financial Document',
        'description': 'Financial knowledge documents',
        'actions': {
            'read': {},
        },
        'attributes': {
            'doc_type': {
                'type': 'string',
                'description': 'Type of financial document',
            },
            'classification': {
                'type': 'string',
                'description': 'Document classification level',
            },
            'clearance_required': {
                'type': 'string',
                'description': 'Required clearance level to access',
            },
        },
    },
    {
        'key': 'financial_response',
        'name': 'Financial Response',
        'description': 'AI-generated response content',
        'actions': {
            'requires_disclaimer': {},
        },
        'attributes': {
            'contains_advice': {
                'type': 'bool',
                'description': 'Whether the response contains financial advice',
            },
            'risk_level': {
                'type': 'string',
                'description': 'Risk level of the response',
            },
        },
    },
    {
        'key': 'portfolio',
        'name': 'Investment Portfolio',
        'description': 'User investment portfolio',
        'actions': {
            'update': {},
            'read': {},
            'analyze': {},
        },
        'attributes': {
            'owner_id': {
                'type': 'string',
                'description': 'Portfolio owner ID',
            },
            'value_tier': {
                'type': 'string',
                'description': 'Portfolio value classification',
            },
        },
    },
]

# Define user attributes
user_attributes = [
    {
        'key': 'clearance_level',
        'type': 'string',
        'description': "User's security clearance level (low, high)",
    },
    {
        'key': 'ai_advice_opted_in',
        'type': 'bool',
        'description': 'Whether user has opted in to receive AI-generated advice',
    },
]

# Define user sets with their attributes
user_sets = [
    {
        'key': 'opted_in_users',
        'name': 'AI Advice Opted-in Users',
        'description': 'Users who have consented to AI-generated advice',
        'type': 'userset',
        'conditions': {'allOf': [{'user.ai_advice_opted_in': {'equals': True}}]},
    },
    {
        'key': 'high_clearance_users',
        'name': 'High Clearance Users',
        'description': 'Users with high-level document access',
        'type': 'userset',
        'conditions': {'allOf': [{'user.clearance_level': {'equals': 'high'}}]},
    },
]

# Define resource sets based on classification
resource_sets = [
    {
        'key': 'confidential_docs',
        'type': 'resourceset',
        'resource_id': 'financial_document',
        'name': 'Confidential Documents',
        'description': 'Documents with confidential classification',
        'conditions': {'allOf': [{'resource.classification': {'equals': 'confidential'}}]},
    },
    {
        'key': 'finance_advice',
        'type': 'resourceset',
        'resource_id': 'financial_advice',
        'name': 'Financial Advice',
        'description': 'Financial advice with ai content',
        'conditions': {'allOf': [{'resource.is_ai_generated': {'equals': True}}]},
    },
]

# Define condition set rules to link user sets with resource sets
condition_set_rules = [
    {
        'user_set': 'opted_in_users',
        'permission': 'financial_advice:receive',
        'resource_set': 'finance_advice',
    },
    {
        'user_set': 'high_clearance_users',
        'permission': 'financial_document:read',
        'resource_set': 'confidential_docs',
    },
]

# Define roles with ABAC rules
roles = [
    {'name': 'restricted_user'},
    {
        'name': 'premium_user',
        'permissions': [
            {
                'resource': 'financial_advice',
                'actions': ['receive'],
                'attributes': {'is_ai_generated': ['true', 'false']},
                'condition_sets': ['opt_in_check', 'risk_level_check'],
            },
            {
                'resource': 'financial_document',
                'actions': ['read'],
                'condition_sets': ['document_clearance'],
            },
            {
                'resource': 'portfolio',
                'actions': ['update', 'read', 'analyze'],
                'attributes': {'value_tier': ['premium', 'standard']},
            },
        ],
    },
]

# Define example users with their attributes
example_users = [
    {
        'key': 'user@example.com',
        'email': 'user@example.com',
        'first_name': 'Example',
        'last_name': 'User',
        'attributes': {
            'clearance_level': 'high',
            'ai_advice_opted_in': True,
        },
        'role': 'premium_user',
    },
    {
        'key': 'restricted@example.com',
        'email': 'restricted@example.com',
        'first_name': 'Restricted',
        'last_name': 'User',
        'attributes': {
            'clearance_level': 'low',
            'ai_advice_opted_in': False,
        },
        'role': 'restricted_user',
    },
]


async def create_resources(permit: Permit) -> None:
    """Create resources in Permit.io."""
    print('\nCreating resources...')
    for resource in resources:
        try:
            print(f'\nAttempting to create resource: {resource["name"]}')
            print(f'Resource config: {resource}')
            await permit.api.resources.create(ResourceCreate(**resource))
            print(f'✓ Successfully created resource: {resource["name"]}')
        except Exception as e:
            print(f'✗ Failed to create resource {resource["name"]}')
            print(f'Error details: {str(e)}')
            raise


async def create_user_attributes(permit: Permit) -> None:
    """Create user attributes in Permit.io."""
    print('\nCreating user attributes...')
    for attr in user_attributes:
        try:
            print(f'\nAttempting to create user attribute: {attr["key"]}')
            print(f'Attribute config: {attr}')
            await permit.api.resource_attributes.create('__user', ResourceAttributeCreate(**attr))
            print(f'✓ Successfully created user attribute: {attr["key"]}')
        except Exception as e:
            print(f'✗ Failed to create user attribute {attr["key"]}')
            print(f'Error details: {str(e)}')
            raise


async def create_roles(permit: Permit) -> None:
    """Create roles in Permit.io."""
    print('\nCreating roles...')
    for role in roles:
        role_name = str(role.get('name', ''))
        try:
            print(f'\nAttempting to create role: {role_name}')
            permissions: list[str] = []
            if isinstance(role, dict) and 'permissions' in role:
                for permission in role['permissions']:
                    if isinstance(permission, dict) and 'actions' in permission:
                        actions = permission.get('actions', [])
                        if isinstance(actions, list):
                            for action in actions:
                                if isinstance(permission.get('resource'), str):
                                    permissions.append(f'{permission["resource"]}:{action}')

            role_data = RoleCreate(
                name=role_name,
                key=role_name.lower().replace(' ', '_'),
                permissions=permissions,
                description=f'Role for {role_name} with ABAC rules',
            )
            await permit.api.roles.create(role_data)
            print(f'✓ Successfully created role: {role_name}')
        except Exception as e:
            print(f'✗ Failed to create role {role_name}')
            print(f'Error details: {str(e)}')
            raise


async def create_condition_sets(permit: Permit) -> None:
    """Create user and resource sets in Permit.io."""
    print('\nCreating user and resource sets...')
    for user_set in user_sets:
        try:
            await permit.api.condition_sets.create(ConditionSetCreate(**user_set))
        except Exception as e:
            print(f'Error creating user set: {str(e)}')
            raise

    for resource_set in resource_sets:
        try:
            await permit.api.condition_sets.create(ConditionSetCreate(**resource_set))
        except Exception as e:
            print(f'Error creating resource set: {str(e)}')
            raise


async def create_permit_config():
    """Create all required configurations in Permit.io."""
    try:
        print('\n=== Starting Permit.io Configuration ===\n')

        await create_resources(permit)
        await create_user_attributes(permit)
        await create_roles(permit)
        await create_condition_sets(permit)

        print('\n=== Configuration completed successfully ===\n')
    except Exception as e:
        print('\n✗ Configuration failed')
        print(f'Final error: {str(e)}')
        raise


if __name__ == '__main__':
    asyncio.run(create_permit_config())
