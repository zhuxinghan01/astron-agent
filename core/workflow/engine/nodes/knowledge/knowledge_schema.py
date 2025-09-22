"""
JSON Schema definition for knowledge base node configuration.

This schema defines the structure and validation rules for knowledge base nodes,
including input/output specifications and node parameters for knowledge retrieval.
"""

knowledge_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "pattern": "^knowledge-base::[0-9a-zA-Z-]+",
            "description": "Unique identifier for the knowledge base node",
        },
        "data": {
            "type": "object",
            "required": ["nodeMeta", "inputs", "outputs", "nodeParam"],
            "description": "Node configuration data",
            "properties": {
                "nodeMeta": {
                    "type": "object",
                    "description": "Node metadata information",
                    "properties": {
                        "nodeType": {
                            "type": "string",
                            "description": "Type of the node",
                        },
                        "aliasName": {
                            "type": "string",
                            "description": "Human-readable name for the node",
                        },
                    },
                },
                "inputs": {
                    "type": "array",
                    "minItems": 0,
                    "description": "Input port definitions for the node",
                    "items": {
                        "type": "object",
                        "required": ["name", "schema"],
                        "properties": {
                            "name": {
                                "type": "string",
                                "minLength": 1,
                                "description": "Name of the input port",
                            },
                            "schema": {
                                "type": "object",
                                "required": ["type", "value"],
                                "description": "Schema definition for the input value",
                                "properties": {
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
                                        "description": "Data type of the input value",
                                    },
                                    "value": {
                                        "type": "object",
                                        "description": "Value specification for the input",
                                        "properties": {
                                            "type": {
                                                "type": "string",
                                                "enum": ["ref", "literal"],
                                                "description": "Value type: reference to another node or literal value",
                                            },
                                            "content": {
                                                "anyOf": [
                                                    {
                                                        "type": "object",
                                                        "required": ["nodeId", "name"],
                                                        "description": "Reference to another node's output",
                                                        "properties": {
                                                            "nodeId": {
                                                                "type": "string",
                                                                "minLength": 1,
                                                                "description": "ID of the referenced node",
                                                            },
                                                            "name": {
                                                                "type": "string",
                                                                "minLength": 1,
                                                                "description": "Name of the referenced output",
                                                            },
                                                        },
                                                    },
                                                    {
                                                        "type": "string",
                                                        "minLength": 1,
                                                        "description": "String literal value",
                                                    },
                                                    {
                                                        "type": "integer",
                                                        "description": "Integer literal value",
                                                    },
                                                    {
                                                        "type": "boolean",
                                                        "description": "Boolean literal value",
                                                    },
                                                    {
                                                        "type": "number",
                                                        "description": "Number literal value",
                                                    },
                                                    {
                                                        "type": "array",
                                                        "description": "Array literal value",
                                                    },
                                                    {
                                                        "type": "object",
                                                        "description": "Object literal value",
                                                    },
                                                ],
                                                "description": "Content of the value (reference or literal)",
                                            },
                                        },
                                    },
                                },
                            },
                        },
                    },
                },
                "outputs": {
                    "type": "array",
                    "minItems": 0,
                    "description": "Output port definitions for the node",
                    "items": {
                        "type": "object",
                        "required": ["name", "schema"],
                        "properties": {
                            "name": {
                                "type": "string",
                                "minLength": 1,
                                "description": "Name of the output port",
                            },
                            "required": {
                                "type": "boolean",
                                "description": "Whether this output is required",
                            },
                            "schema": {
                                "type": "object",
                                "required": ["type"],
                                "description": "Schema definition for the output value",
                                "properties": {
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
                                        "description": "Data type of the output value",
                                    }
                                },
                            },
                        },
                    },
                },
                "nodeParam": {
                    "type": "object",
                    "required": ["repoId"],
                    "description": "Node-specific parameters for knowledge base configuration",
                    "properties": {
                        "topN": {
                            "type": "string",
                            "minLength": 1,
                            "description": "Number of top results to retrieve from knowledge base",
                        },
                        "ragType": {
                            "type": "string",
                            "description": "Type of RAG (Retrieval-Augmented Generation) to use",
                        },
                        "repoId": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of repository IDs to search in",
                        },
                        "score": {
                            "type": "number",
                            "description": "Minimum similarity threshold for results",
                        },
                    },
                },
            },
        },
    },
}
