"""
JSON Schema definition for start node configuration.

This schema defines the structure and validation rules for start nodes
in the workflow engine. Start nodes serve as entry points for workflow
execution and define the input/output variables that can be used
throughout the workflow.
"""

spark_start_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["id", "data"],
    "properties": {
        # Unique identifier for the start node, must follow the pattern node-start::<id>
        "id": {"type": "string", "pattern": "^node-start::[0-9a-zA-Z-]+"},
        "data": {
            "type": "object",
            "required": ["nodeMeta", "inputs", "outputs", "nodeParam"],
            "properties": {
                # Node metadata containing type and display information
                "nodeMeta": {
                    "type": "object",
                    "properties": {
                        "nodeType": {
                            "type": "string"
                        },  # Type of the node (e.g., "start")
                        "aliasName": {
                            "type": "string"
                        },  # Human-readable name for the node
                    },
                },
                # Input variables array (typically empty for start nodes)
                "inputs": {"type": "array", "minItems": 0},
                # Output variables that this start node can provide to the workflow
                "outputs": {
                    "type": "array",
                    "minItems": 0,
                    "items": {
                        "type": "object",
                        "required": ["name", "schema"],
                        "properties": {
                            "name": {"type": "string", "minLength": 1},  # Variable name
                            "required": {
                                "type": "boolean"
                            },  # Whether this variable is required
                            "schema": {
                                "type": "object",
                                "required": ["type"],
                                "properties": {
                                    "type": {
                                        "type": "string",
                                        "enum": [
                                            "string",  # Text data
                                            "boolean",  # True/false values
                                            "integer",  # Whole numbers
                                            "number",  # Decimal numbers
                                            "array",  # List of items
                                            "object",  # Complex data structures
                                        ],
                                    }
                                },
                            },
                        },
                    },
                },
                # Additional node-specific parameters
                "nodeParam": {"type": "object"},
            },
        },
    },
}
