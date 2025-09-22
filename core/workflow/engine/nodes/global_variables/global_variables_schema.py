"""
Global Variables Node Schema Definition

This module defines the JSON schema for global variables nodes in the workflow system.
The schema validates the structure and data types for global variable node configurations,
including input/output definitions and node parameters for 'set' and 'get' operations.
"""

variables_schemas = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["id", "data"],
    "properties": {
        # Node identifier with specific pattern for variable nodes
        "id": {"type": "string", "pattern": "^node-variable::[0-9a-zA-Z-]+"},
        "data": {
            "type": "object",
            "required": ["nodeMeta", "inputs", "outputs", "nodeParam"],
            "properties": {
                # Node metadata information
                "nodeMeta": {
                    "type": "object",
                    "properties": {
                        "nodeType": {"type": "string"},  # Type of the node
                        "aliasName": {
                            "type": "string"
                        },  # Human-readable name for the node
                    },
                },
                # Input variable definitions
                "inputs": {
                    "type": "array",
                    "minItems": 0,
                    "items": {
                        "type": "object",
                        "required": ["name", "schema"],
                        "properties": {
                            "name": {
                                "type": "string",
                                "minLength": 0,
                            },  # Input variable name
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
                                    "value": {
                                        "type": "object",
                                        "required": ["type", "content"],
                                        "properties": {
                                            # Value type: reference to another node or literal value
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
                                                    # Literal values of various types
                                                    {"type": "string", "minLength": 1},
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
                # Output variable definitions
                "outputs": {
                    "type": "array",
                    "minItems": 0,
                    "items": {
                        "type": "object",
                        "required": ["name", "schema"],
                        "properties": {
                            "name": {
                                "type": "string",
                                "minLength": 0,
                            },  # Output variable name
                            "required": {
                                "type": "boolean"
                            },  # Whether this output is required
                            "schema": {
                                "type": "object",
                                "required": ["type"],
                                "properties": {
                                    # Data type of the output variable
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
                                    }
                                },
                            },
                        },
                    },
                },
                # Node-specific parameters
                "nodeParam": {
                    "type": "object",
                    "required": ["method", "flowId"],
                    "properties": {
                        # Operation method: "set" to store variables, "get" to retrieve variables
                        "method": {"type": "string", "enum": ["set", "get"]},
                        # Flow identifier for variable scope
                        "flowId": {"type": "string"},
                    },
                },
            },
        },
    },
}
