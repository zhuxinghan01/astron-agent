"""
JSON Schema definition for plugin tool nodes.

This schema defines the structure and validation rules for plugin tool nodes
in the workflow system. It specifies the required fields, data types, and
constraints for plugin node configuration.
"""

plugin_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        # Node identifier with plugin prefix pattern
        "id": {"type": "string", "pattern": "^plugin::[0-9a-zA-Z-]+"},
        "data": {
            "type": "object",
            "required": ["nodeMeta", "inputs", "outputs", "nodeParam"],
            "properties": {
                # Node metadata configuration
                "nodeMeta": {
                    "type": "object",
                    "properties": {
                        "nodeType": {"type": "string"},
                        "aliasName": {"type": "string"},
                    },
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
                                    # Supported data types for input parameters
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
                                            # Value source type: reference or literal
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
                # Output parameter definitions
                "outputs": {
                    "type": "array",
                    "minItems": 0,
                    "items": {
                        "type": "object",
                        "required": ["name", "schema"],
                        "properties": {
                            "name": {"type": "string", "minLength": 1},
                            "required": {"type": "boolean"},
                            "schema": {
                                "type": "object",
                                "required": ["type"],
                                "properties": {
                                    # Supported data types for output parameters
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
                # Plugin-specific node parameters
                "nodeParam": {
                    "type": "object",
                    "required": ["pluginId", "appId", "operationId"],
                    "properties": {
                        # Plugin tool identifier
                        "pluginId": {"type": "string", "minLength": 1},
                        # Application identifier
                        "appId": {"type": "string", "minLength": 1},
                        # Specific operation identifier within the plugin
                        "operationId": {"minLength": 1, "type": "string"},
                        # Optional version specification
                        "version": {"type": "string"},
                    },
                },
            },
        },
    },
}
