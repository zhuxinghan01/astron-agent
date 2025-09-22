# JSON Schema definition for Spark Decision Node configuration
# This schema validates the structure and constraints for decision node parameters
spark_decision_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        # Node ID must follow the pattern: decision-making::[alphanumeric-dash]
        "id": {"type": "string", "pattern": "^decision-making::[0-9a-zA-Z-]+"},
        "data": {
            "type": "object",
            "required": ["nodeMeta", "inputs", "outputs", "nodeParam"],
            "properties": {
                # Node metadata containing type and alias information
                "nodeMeta": {
                    "type": "object",
                    "properties": {
                        "nodeType": {"type": "string"},
                        "aliasName": {"type": "string"},
                    },
                },
                # Input definitions for the decision node
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
                                        "required": ["type", "content"],
                                        "properties": {
                                            # Value can be either a reference or literal
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
                # Output definitions for the decision node (limited to 1 output)
                "outputs": {
                    "type": "array",
                    "minItems": 0,
                    "maxItems": 1,
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
                                    # Decision node output is always a string (selected intent name)
                                    "type": {"type": "string", "enum": ["string"]}
                                },
                            },
                        },
                    },
                },
                # Node parameters specific to decision node configuration
                "nodeParam": {
                    "type": "object",
                    "required": [
                        "model",
                        "domain",
                        "appId",
                        "apiKey",
                        "apiSecret",
                        "intentChains",
                    ],
                    "properties": {
                        # LLM model configuration
                        "model": {"type": "string", "minLength": 1},
                        "url": {"type": "string"},
                        "domain": {"type": "string"},
                        "temperature": {
                            "type": "number",
                            "exclusiveMinimum": 0,
                            "maximum": 1,
                        },
                        # API credentials for LLM service
                        "appId": {"type": "string", "minLength": 1, "maxLength": 10},
                        "apiKey": {"type": "string"},
                        "apiSecret": {"type": "string"},
                        "maxTokens": {"type": "integer", "exclusiveMinimum": 0},
                        "uid": {"type": "string"},
                        # Prompt and template configuration
                        "template": {"type": "string"},
                        "promptPrefix": {"type": "string"},
                        # Chat history configuration
                        "enableChatHistoryV2": {
                            "type": "object",
                            "properties": {
                                "isEnabled": {"type": "boolean"},
                                "rounds": {"type": "integer", "exclusiveMinimum": 0},
                            },
                        },
                        "extraParams": {"type": "object"},
                        # Intent chain definitions for decision routing
                        "intentChains": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["id", "name", "description", "intentType"],
                                "properties": {
                                    # Intent ID must follow pattern: intent-one-of::[alphanumeric-dash]
                                    "id": {
                                        "type": "string",
                                        "pattern": "^intent-one-of::[0-9a-zA-Z-]+",
                                    },
                                    "name": {"type": "string", "minLength": 1},
                                    "description": {"type": "string", "minLength": 1},
                                    # Intent type: 1=default, 2=regular
                                    "intentType": {"type": "integer", "enum": [1, 2]},
                                },
                            },
                        },
                    },
                },
            },
        },
    },
}
