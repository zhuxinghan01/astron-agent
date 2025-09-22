"""
JSON Schema definition for If-Else node configuration.

This module defines the schema structure for validating if-else node configurations,
including node metadata, input/output definitions, and branch conditions.
"""

import jsonschema  # type: ignore

# JSON Schema for validating if-else node configuration
if_else_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        # Node unique identifier with if-else prefix
        "id": {"type": "string", "pattern": "^if-else::[0-9a-zA-Z-]+"},
        "data": {
            "type": "object",
            "properties": {
                # Node metadata information
                "nodeMeta": {
                    "type": "object",
                    "properties": {
                        "nodeType": {"type": "string", "minLength": 1},
                        "aliasName": {"type": "string", "minLength": 1},
                    },
                    "required": ["nodeType", "aliasName"],
                },
                # Input variable definitions for the node
                "inputs": {
                    "type": "array",
                    "minItems": 0,
                    "items": {
                        "type": "object",
                        "required": ["name", "id", "schema"],
                        "properties": {
                            "name": {"type": "string", "minLength": 1},
                            "id": {"type": "string"},
                            "schema": {
                                "type": "object",
                                "required": ["type", "value"],
                                "properties": {
                                    # Data type of the input variable
                                    "type": {
                                        "type": "string",
                                        "enum": [
                                            "string",
                                            "boolean",
                                            "integer",
                                            "number",
                                            "array",
                                            "object",
                                        ],
                                    },
                                    # Value definition (reference or literal)
                                    "value": {
                                        "type": "object",
                                        "properties": {
                                            "type": {
                                                "type": "string",
                                                "enum": ["ref", "literal"],
                                            },
                                            "content": {
                                                "anyOf": [
                                                    # Reference to another node's output
                                                    {
                                                        "type": "object",
                                                        "required": ["nodeId", "name"],
                                                        "properties": {
                                                            "nodeId": {
                                                                "type": "string",
                                                                "minLength": 1,
                                                            },
                                                            "name": {
                                                                "type": "string",
                                                                "minLength": 1,
                                                            },
                                                        },
                                                    },
                                                    # Literal values
                                                    {"type": "string"},
                                                    {"type": "integer"},
                                                    {"type": "boolean"},
                                                    {"type": "number"},
                                                    {"type": "array"},
                                                    {"type": "object"},
                                                ]
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
                # Output variable names from the node
                "outputs": {
                    "type": "array",
                    "minItems": 0,
                    "items": {"type": "string"},
                },
                # Node-specific parameters for if-else configuration
                "nodeParam": {
                    "type": "object",
                    "required": ["cases"],
                    "properties": {
                        # Array of branch cases to evaluate
                        "cases": {
                            "type": "array",
                            "minItems": 2,
                            "items": {
                                "type": "object",
                                "required": [
                                    "id",
                                    "level",
                                    "logicalOperator",
                                    "conditions",
                                ],
                                "properties": {
                                    # Branch unique identifier
                                    "id": {
                                        "type": "string",
                                        "pattern": "^branch_one_of::[0-9a-zA-Z-]+",
                                    },
                                    # Priority level for branch execution order
                                    "level": {"type": "integer", "minimum": 1},
                                    # Logical operator to combine conditions
                                    "logicalOperator": {
                                        "type": "string",
                                        "enum": ["and", "or"],
                                    },
                                    # Array of conditions to evaluate
                                    "conditions": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                # Index of left operand variable
                                                "leftVarIndex": {"type": "string"},
                                                # Index of right operand variable
                                                "rightVarIndex": {"type": "string"},
                                                # Comparison operator to use
                                                "compareOperator": {
                                                    "type": "string",
                                                    "enum": [
                                                        # String/array operators
                                                        "contains",
                                                        "not_contains",
                                                        "empty",
                                                        "not_empty",
                                                        "is",
                                                        "is_not",
                                                        "start_with",
                                                        "end_with",
                                                        # Numeric operators
                                                        "eq",
                                                        "ne",
                                                        "gt",
                                                        "ge",
                                                        "lt",
                                                        "le",
                                                        # Null operators
                                                        "null",
                                                        "not_null",
                                                    ],
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        }
                    },
                },
            },
        },
    },
}

# Test the schema validation with a sample configuration
if __name__ == "__main__":
    # Sample if-else node configuration for testing
    node_body = {
        "id": "if-else::831c1984-9de2-4b55-9e0d-d23a87282539",
        "data": {
            "nodeMeta": {"nodeType": "分支节点", "aliasName": "if-else节点"},
            "inputs": [
                {
                    "name": "str1",
                    "id": "hadhfadhdfahudfhadi",
                    "schema": {
                        "type": "string",
                        "value": {
                            "type": "ref",
                            "content": {
                                "nodeId": "node-start::6fca1c6b-d6b7-4cd3-9b3c-be735f3756ef",
                                "name": "input",
                            },
                        },
                    },
                },
                {
                    "name": "str1_compare_value",
                    "id": "hadhfadhdfahudfhadi2",
                    "schema": {
                        "type": "string",
                        "value": {"type": "literal", "content": "hello"},
                    },
                },
                {
                    "name": "str2",
                    "id": "hadhfadhdfahudfhadi3",
                    "schema": {
                        "type": "string",
                        "value": {
                            "type": "ref",
                            "content": {
                                "nodeId": "node-start::6fca1c6b-d6b7-4cd3-9b3c-be735f3756ef",
                                "name": "input",
                            },
                        },
                    },
                },
                {
                    "name": "str2_compare_value",
                    "id": "hadhfadhdfahudfhadi4",
                    "schema": {
                        "type": "string",
                        "value": {
                            "type": "ref",
                            "content": {
                                "nodeId": "node-start::6fca1c6b-d6b7-4cd3-9b3c-be735f3756ef",
                                "name": "input",
                            },
                        },
                    },
                },
            ],
            "outputs": [],
            "nodeParam": {
                "cases": [
                    {
                        "id": "branch_one_of::db379de3-dc37-4bf6-a47f-103a1375a64f",
                        "level": 1,
                        "logicalOperator": "and",
                        "conditions": [
                            {
                                "leftVarIndex": "hadhfadhdfahudfhadi",
                                "rightVarIndex": "hadhfadhdfahudfhadi1",
                                "compareOperator": "start_with",
                            },
                            {
                                "leftVarIndex": "hadhfadhdfahudfhadi2",
                                "rightVarIndex": "hadhfadhdfahudfhadi3",
                                "compareOperator": "end_with",
                            },
                        ],
                    },
                    {
                        "id": "branch_one_of::db379de3-dc37-4bf6-a47f-375a64f103a1",
                        "level": 2,
                        "logicalOperator": "and",
                        "conditions": [],
                    },
                ]
            },
        },
    }
    # Validate the sample configuration against the schema
    res = list(jsonschema.Draft7Validator(if_else_schema).iter_errors(node_body))
    print(res)
