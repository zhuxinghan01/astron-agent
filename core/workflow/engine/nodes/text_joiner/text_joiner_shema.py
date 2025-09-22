# JSON Schema definition for TextJoinerNode configuration
# This schema validates the structure and constraints for TextJoinerNode instances
# including node metadata, input/output definitions, and processing parameters
text_joiner_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["id", "data"],
    "properties": {
        # Node identifier with specific pattern for text-joiner nodes
        "id": {"type": "string", "pattern": "^text-joiner::[0-9a-zA-Z-]+"},
        "data": {
            "type": "object",
            "required": ["nodeMeta", "inputs", "outputs", "nodeParam"],
            "properties": {
                # Node metadata containing type and display information
                "nodeMeta": {
                    "type": "object",
                    "properties": {
                        "nodeType": {"type": "string"},  # Type identifier for the node
                        "aliasName": {
                            "type": "string"
                        },  # Human-readable name for the node
                    },
                },
                # Input definitions for the text joiner node
                "inputs": {
                    "type": "array",
                    "minItems": 0,
                    "items": {
                        "type": "object",
                        "required": ["name", "schema"],
                        "properties": {
                            "name": {
                                "type": "string",
                                "minLength": 1,
                            },  # Input variable name
                            "schema": {
                                "type": "object",
                                "required": ["type", "value"],
                                "properties": {
                                    # Data type for the input value
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
                                    # Value definition for input data
                                    "value": {
                                        "type": "object",
                                        "required": ["type", "content"],
                                        "properties": {
                                            # Value type: reference to another node or literal value
                                            "type": {
                                                "type": "string",
                                                "enum": ["ref", "literal"],
                                            },
                                            # Content can be a reference to another node or a literal value
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
                # Output definitions for the text joiner node
                "outputs": {
                    "type": "array",
                    "minItems": 0,
                    "items": {
                        "type": "object",
                        "required": ["name", "schema"],
                        "properties": {
                            "name": {
                                "type": "string",
                                "minLength": 1,
                            },  # Output variable name
                            "required": {
                                "type": "boolean"
                            },  # Whether this output is required
                            "schema": {
                                "type": "object",
                                "required": ["type"],
                                "properties": {
                                    # Data type for the output value
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
                # Node-specific parameters for text processing configuration
                "nodeParam": {
                    "type": "object",
                    "properties": {
                        "mode": {
                            "type": "integer",
                            "enum": [0, 1],
                        },  # Processing mode: 0=JOIN, 1=SEPARATE
                        "prompt": {
                            "type": "string"
                        },  # Template string for text concatenation
                        "separator": {
                            "type": "string"
                        },  # Delimiter for text separation
                    },
                },
            },
        },
    },
}
