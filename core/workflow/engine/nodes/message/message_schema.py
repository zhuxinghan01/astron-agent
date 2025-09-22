"""
JSON Schema definition for message node configuration.

This schema defines the structure and validation rules for message node
configuration in the workflow engine. It specifies the required fields,
data types, and constraints for message node parameters.
"""

message_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        # Node identifier with message prefix pattern
        "id": {"type": "string", "pattern": "^message::[0-9a-zA-Z-]+"},
        "data": {
            "type": "object",
            "properties": {
                # Node metadata including type and alias
                "nodeMeta": {
                    "type": "object",
                    "properties": {
                        "nodeType": {"type": "string", "minLength": 1},
                        "aliasName": {"type": "string", "minLength": 1},
                    },
                    "required": ["nodeType", "aliasName"],
                },
                # Input parameter definitions
                "inputs": {
                    "type": "array",
                    "minItems": 0,
                    "items": {
                        "type": "object",
                        "required": ["name", "schema"],
                        "properties": {
                            "name": {"type": "string", "minLength": 1},
                            "schema": {
                                "type": "object",
                                "required": ["type", "value"],
                                "properties": {
                                    # Supported data types for input values
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
                                        "properties": {
                                            # Value reference type: ref or literal
                                            "type": {
                                                "type": "string",
                                                "enum": ["ref", "literal"],
                                            },
                                            # Content can be node reference or literal value
                                            "content": {
                                                "anyOf": [
                                                    # Node reference object
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
                # Output parameter definitions
                "outputs": {
                    "type": "array",
                    "minItems": 0,
                    "items": {
                        "type": "object",
                        "required": ["schema"],
                        "properties": {
                            "schema": {
                                "type": "object",
                                "required": ["type"],
                                "properties": {
                                    # Supported output data types
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
                            }
                        },
                    },
                },
                # Node-specific parameters
                "nodeParam": {
                    "type": "object",
                    "required": ["template"],
                    "properties": {
                        "template": {"type": "string"},
                        "startFrameEnabled": {"type": "boolean"},
                        "streamOutput": {"type": "boolean"},
                    },
                },
            },
        },
    },
}
