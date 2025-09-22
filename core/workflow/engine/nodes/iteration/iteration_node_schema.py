# JSON Schema for iteration node configuration
# Defines the structure and validation rules for iteration nodes in the workflow engine
iteration_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "id": {"type": "string", "pattern": "^iteration::[0-9a-zA-Z-]+"},
        "data": {
            "type": "object",
            "properties": {
                "nodeMeta": {
                    "type": "object",
                    "properties": {
                        "nodeType": {"type": "string", "minLength": 1},
                        "aliasName": {"type": "string", "minLength": 1},
                    },
                    "required": ["nodeType", "aliasName"],
                },
                "inputs": {
                    "type": "array",
                    "minItems": 1,
                    "maxItems": 1,
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
                                            "array",
                                        ],
                                    },
                                    "value": {
                                        "type": "object",
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
                                            "array",
                                        ],
                                    }
                                },
                            },
                        },
                    },
                },
                "nodeParam": {
                    "type": "object",
                    "properties": {"IterationStartNodeId": {"type": "string"}},
                },
            },
        },
    },
}

# JSON Schema for iteration start node configuration
# Defines the structure and validation rules for iteration start nodes
iteration_start_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["id", "data"],
    "properties": {
        "id": {"type": "string", "pattern": "^iteration-node-start::[0-9a-zA-Z-]+"},
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
                "inputs": {"type": "array", "minItems": 0},
                "outputs": {
                    "type": "array",
                    "minItems": 0,
                    "items": {
                        "type": "object",
                        "required": ["name", "schema"],
                        "properties": {
                            "name": {"type": "string", "minLength": 1},
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
                "nodeParam": {"type": "object"},
            },
        },
    },
}

# JSON Schema for iteration end node configuration
# Defines the structure and validation rules for iteration end nodes
iteration_end_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["id", "data"],
    "properties": {
        "id": {"type": "string", "pattern": "^iteration-node-end::[0-9a-zA-Z-]+"},
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
                "outputs": {"type": "array", "minItems": 0},
                "nodeParam": {"type": "object"},
            },
        },
    },
}
