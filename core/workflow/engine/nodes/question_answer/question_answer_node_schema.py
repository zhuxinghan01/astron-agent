"""
JSON Schema validation for question-answer node configuration

This module defines the schema structure for validating question-answer node
configuration data, including node metadata, inputs, outputs, and parameters.
"""

import json

import jsonschema  # type: ignore
from jsonschema import validate

# JSON Schema definition for question-answer node validation
question_answer_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["id", "data"],
    "properties": {
        "id": {"type": "string", "pattern": "^question-answer::[0-9a-zA-Z-]+"},
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
                    # "minItems": 1,
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
                                            "int",
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
                    "required": [
                        "question",
                        "answerType",
                        "timeout",
                        "needReply",
                        "model",
                        "domain",
                        "appId",
                        "url",
                        "apiKey",
                        "apiSecret",
                    ],
                    "properties": {
                        "question": {"type": "string"},
                        "answerType": {"type": "string", "enum": ["option", "direct"]},
                        "timeout": {
                            "type": "number",
                            "exclusiveMinimum": 1,
                            "maximum": 5,
                        },
                        "needReply": {"type": "boolean"},
                        "directAnswer": {
                            "type": "object",
                            "required": ["handleResponse", "maxRetryCounts"],
                            "properties": {
                                "handleResponse": {"type": "boolean"},
                                "maxRetryCounts": {
                                    "type": "number",
                                    "exclusiveMinimum": 1,
                                    "maximum": 5,
                                },
                            },
                        },
                        "optionAnswer": {
                            "type": "array",
                            "minItems": 1,
                            "items": {
                                "type": "object",
                                "required": [
                                    "id",
                                    "name",
                                    "type",
                                    "content_type",
                                    "content",
                                ],
                                "properties": {
                                    "id": {"type": "string"},
                                    "name": {
                                        "type": "string",
                                        "anyOf": [
                                            {"pattern": "^[A-Z]$"},
                                            {"const": "default"},
                                        ],
                                    },
                                    "type": {"type": "number", "enum": [1, 2]},
                                    "content_type": {"type": "string"},
                                    "content": {"type": "string"},
                                },
                            },
                        },
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
    Main function for testing schema validation

    This function reads a sample JSON file and validates it against
    the question_answer_schema to ensure the schema is working correctly.
    """
    # JSON data
    with open("question_answer_schema.json", "r", encoding="utf-8") as file:
        data = file.read()
    # JSON Schema
    schema = question_answer_schema

    # Validation
    try:
        validate(instance=json.loads(data), schema=schema)
        print("Data conforms to JSON Schema")
    except jsonschema.exceptions.ValidationError as err:
        print("Data does not conform to JSON Schema", err)
