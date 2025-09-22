# JSON Schema definition for Spark LLM node configuration
# This schema validates the structure and types of Spark LLM node parameters
spark_llm_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["id", "data"],
    "properties": {
        "id": {"type": "string", "pattern": "^spark-llm::[0-9a-zA-Z-]+"},
        "data": {
            "type": "object",
            "required": ["nodeMeta", "inputs", "outputs", "nodeParam"],
            "properties": {
                "nodeMeta": {
                    "type": "object",
                    "properties": {
                        "nodeType": {"type": "string"},
                        "aliasName": {"type": "string"},
                    },
                },
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
                "nodeParam": {
                    "type": "object",
                    "required": [
                        "model",
                        "domain",
                        "appId",
                        "apiKey",
                        "apiSecret",
                        "template",
                    ],
                    "properties": {
                        "model": {"type": "string", "minLength": 1},
                        "url": {"type": "string"},
                        "domain": {"type": "string"},
                        "temperature": {
                            "type": "number",
                            "exclusiveMinimum": 0,
                            "maximum": 1,
                        },
                        "appId": {"type": "string", "minLength": 1, "maxLength": 10},
                        "apiKey": {"type": "string"},
                        "apiSecret": {"type": "string"},
                        "maxTokens": {"type": "integer", "exclusiveMinimum": 0},
                        "uid": {"type": "string"},
                        "template": {"type": "string"},
                        "systemTemplate": {"type": "string"},
                        "enableChatHistoryV2": {
                            "type": "object",
                            "properties": {
                                "isEnabled": {"type": "boolean"},
                                "rounds": {"type": "integer", "exclusiveMinimum": 0},
                            },
                        },
                        "respFormat": {"type": "integer", "enum": [0, 1, 2]},
                        "searchDisable": {"type": "boolean"},
                        "extraParams": {"type": "object"},
                    },
                },
            },
        },
    },
}
