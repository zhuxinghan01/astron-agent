"""
Parameter Extractor Schema Definition

This module defines the JSON schema for parameter extractor nodes,
including validation rules for node configuration, inputs, outputs, and parameters.
"""

import jsonschema  # type: ignore
from jsonschema import validate

# JSON schema definition for parameter extractor node configuration
pe_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["id", "data"],
    "properties": {
        "id": {"type": "string", "pattern": "^extractor-parameter::[0-9a-zA-Z-]+"},
        "data": {
            "type": "object",
            "required": ["nodeMeta", "inputs", "outputs", "nodeParam"],
            "properties": {
                "nodeMeta": {
                    "type": "object",
                    "properties": {
                        "nodeType": {"type": "string", "minLength": 1},
                        "aliasName": {"type": "string", "minLength": 1},
                    },
                },
                "inputs": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["name", "schema"],
                        "properties": {
                            "name": {"type": "string", "minLength": 1},
                            "schema": {
                                "type": "object",
                                "required": ["type", "value"],
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
                                    },
                                    "value": {
                                        "type": "object",
                                        "required": ["type", "content"],
                                        "properties": {
                                            "type": {
                                                "type": "string",
                                                "enum": ["ref", "literal"],
                                            },
                                            "content": {
                                                "anyOf": [
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
                "outputs": {
                    "type": "array",
                    "minItems": 1,
                    "items": {
                        "type": "object",
                        "required": ["name", "schema", "required"],
                        "properties": {
                            "name": {"type": "string", "minLength": 1},
                            "required": {"type": "boolean"},
                            "schema": {
                                "type": "object",
                                "required": ["type", "description"],
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
                                    },
                                    "description": {"type": "string"},
                                },
                            },
                        },
                    },
                },
                "nodeParam": {
                    "type": "object",
                    "required": ["model", "domain", "appId", "apiKey", "apiSecret"],
                    "properties": {
                        "model": {"type": "string"},
                        "url": {"type": "string"},
                        "domain": {"type": "string"},
                        "temperature": {
                            "type": "number",
                            "exclusiveMinimum": 0,
                            "maximum": 1,
                        },
                        "appId": {"type": "string"},
                        "apiKey": {"type": "string"},
                        "apiSecret": {"type": "string"},
                        "maxTokens": {"type": "integer"},
                        "uid": {"type": "string"},
                    },
                },
            },
        },
    },
}

if __name__ == "__main__":
    """
    Test script for validating parameter extractor schema.

    This section contains example data and validation logic for testing
    the parameter extractor schema definition.
    """

    # Example JSON Schema for testing
    schema = {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "schema": {
                "type": "object",
                "properties": {
                    "type": {"type": "string"},
                    "required": {"type": "array", "items": {"type": "string"}},
                    "properties": {
                        "type": "object",
                        "properties": {},
                        "minProperties": 1,
                        "maxProperties": 1,
                    },
                },
                "required": ["type", "properties", "required"],
            },
        },
        "required": ["name", "schema"],
    }

    # Example JSON Data for validation testing
    data = {
        "name": "output",
        "schema": {
            "type": "object",
            "properties": {"1output2": {"type": "string"}},
            "required": ["output"],
        },
    }

    # Validate the example data against the schema
    try:
        validate(instance=data, schema=schema)
        print("Data conforms to JSON Schema")
    except jsonschema.exceptions.ValidationError as err:
        print("Data does not conform to JSON Schema", err)
