"""
JSON Schema definition for Knowledge Pro node configuration.

This schema defines the structure and validation rules for Knowledge Pro node
configuration, including input/output specifications and parameter validation.
"""

knowledge_pro_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        # Node identifier with specific pattern for Knowledge Pro nodes
        "id": {"type": "string", "pattern": "^knowledge-pro-base::[0-9a-zA-Z-]+"},
        "data": {
            "type": "object",
            "required": ["nodeMeta", "inputs", "outputs", "nodeParam"],
            "properties": {
                # Node metadata configuration
                "nodeMeta": {
                    "type": "object",
                    "properties": {
                        "nodeType": {"type": "string"},  # Type of the node
                        "aliasName": {
                            "type": "string"
                        },  # Human-readable name for the node
                    },
                },
                # Input port definitions
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
                            },  # Input port name
                            "schema": {
                                "type": "object",
                                "required": ["type", "value"],
                                "properties": {
                                    # Data type specification
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
                                    # Value definition (reference or literal)
                                    "value": {
                                        "type": "object",
                                        "properties": {
                                            "type": {
                                                "type": "string",
                                                "enum": [
                                                    "ref",
                                                    "literal",
                                                ],  # Reference to another node or literal value
                                            },
                                            "content": {
                                                "anyOf": [
                                                    # Reference to another node output
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
                # Output port definitions
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
                            },  # Output port name
                            "required": {
                                "type": "boolean"
                            },  # Whether this output is required
                            "schema": {
                                "type": "object",
                                "required": ["type"],
                                "properties": {
                                    # Output data type specification
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
                # Node-specific parameters for Knowledge Pro configuration
                "nodeParam": {
                    "$schema": "http://json-schema.org/draft-07/schema#",
                    "type": "object",
                    "properties": {
                        # LLM configuration parameters
                        "model": {
                            "type": "string",
                            "minLength": 1,
                        },  # LLM model identifier
                        "url": {
                            "type": "string",
                            "minLength": 1,
                        },  # Base URL for LLM API
                        "domain": {
                            "type": "string",
                            "minLength": 1,
                        },  # Domain specification
                        "appId": {"type": "string", "minLength": 1},  # Application ID
                        "apiKey": {"type": "string", "minLength": 1},  # API key
                        "apiSecret": {"type": "string", "minLength": 1},  # API secret
                        "temperature": {  # Temperature parameter (0.0-1.0)
                            "type": "number",
                            "exclusiveMinimum": 0,
                            "maximum": 1,
                        },
                        "maxTokens": {
                            "type": "integer",
                            "minimum": 1,
                        },  # Maximum tokens in response
                        "topK": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 6,
                        },  # Top-K parameter
                        "uid": {"type": "string"},  # User identifier (optional)
                        # RAG configuration parameters
                        "ragType": {
                            "type": "integer",
                            "enum": [1, 2],
                        },  # RAG type (1: AGENTIC_RAG, 2: LONG_RAG)
                        "repoIds": {  # Repository IDs to query
                            "type": "array",
                            "items": {"type": "string", "minLength": 1},
                            "minItems": 1,
                        },
                        "repoType": {
                            "type": "integer",
                            "enum": [1, 2],
                        },  # Repository type (1: AIUI_RAG2, 2: CBG_RAG)
                        "docIds": {  # Document IDs (required for CBG_RAG)
                            "type": "array",
                            "items": {"type": "string", "minLength": 1},
                        },
                        "repoTopK": {
                            "type": "integer",
                            "minimum": 1,
                            "maximum": 5,
                        },  # Top documents to retrieve
                        "answerRole": {"type": "string"},  # Answer role specification
                        "score": {"type": "number"},  # Score threshold for relevance
                    },
                    # Required parameters for Knowledge Pro node
                    "required": [
                        "model",  # LLM model identifier
                        "url",  # Base URL for LLM API
                        "domain",  # Domain specification
                        "appId",  # Application ID
                        "apiKey",  # API key
                        "apiSecret",  # API secret
                        "temperature",  # Temperature parameter
                        "maxTokens",  # Maximum tokens
                        "topK",  # Top-K parameter
                        "ragType",  # RAG type
                        "repoIds",  # Repository IDs
                        "repoType",  # Repository type
                        "repoTopK",  # Top documents to retrieve
                    ],
                    # Conditional validation rules
                    "allOf": [
                        {
                            # If repository type is CBG_RAG (2), docIds is required
                            "if": {"properties": {"repoType": {"const": 2}}},
                            "then": {
                                "required": ["docIds"],
                                "properties": {
                                    "docIds": {
                                        "type": "array",
                                        "items": {"type": "string", "minLength": 1},
                                        "minItems": 1,
                                    }
                                },
                            },
                        }
                    ],
                },
            },
        },
    },
}

if __name__ == "__main__":
    """
    Test script for validating Knowledge Pro node configuration.

    This script demonstrates how to use the schema for validating
    node configuration and provides an example configuration.
    """
    import jsonschema  # type: ignore

    # Example node configuration for testing
    node_body = {
        "data": {
            "inputs": [
                {
                    "id": "d27665b7-a8c1-4c3f-8084-cbfd2374ad47",
                    "name": "query",
                    "schema": {
                        "type": "string",
                        "value": {
                            "content": {
                                "id": "84a028b1-afbe-4a7a-9437-d6ffdbc13167",
                                "nodeId": "node-start::28515866-a686-48bb-a2b5-a6f74a869fdd",
                                "name": "AGENT_USER_INPUT",
                            },
                            "type": "ref",
                        },
                    },
                }
            ],
            "nodeMeta": {"aliasName": "知识库 Pro_1", "nodeType": "工具"},
            "nodeParam": {
                "topK": 1,
                "apiKey": "5f93d1890c25748e68a514c62f79b8b1",
                "apiSecret": "ODc3MDhkZjA4M2E4ZDgzODM0MmY4MzZk",
                "ragType": 1,
                "url": "wss://spark-api.cn-huabei-1.xf-yun.com/v2.1/image",
                "docIds": ["b8328cbc68534560a7943302d391b505"],
                "multiMode": True,
                "uid": "1600610195",
                "repoType": 2,
                "isThink": False,
                "repoTopK": 1,
                "domain": "imagev3",
                "appId": "a01c2bc7",
                "temperature": 0.5,
                "maxTokens": 2048,
                "model": "xdeepseekv3",
                "repoIds": [
                    "9e69b8c0840a4f788a21775283acdf53",
                    "c822d34918404415b40cefefff0d3237",
                ],
                "answerRole": "123",
                "serviceId": "image_understandingv3",
            },
            "outputs": [
                {
                    "id": "e219e9c2-e22e-46c2-992c-c017a956f2b6",
                    "name": "output",
                    "required": False,
                    "schema": {"description": "", "type": "string"},
                },
                {
                    "id": "bbe0b22a-1486-4df2-aaa6-180194523246",
                    "name": "result",
                    "required": False,
                    "schema": {
                        "description": "",
                        "items": {
                            "properties": {
                                "chunk": {
                                    "items": {
                                        "properties": {
                                            "chunk_context": {"type": "string"},
                                            "score": {"type": "number"},
                                        },
                                        "type": "object",
                                    },
                                    "type": "array",
                                },
                                "source_id": {"type": "string"},
                            },
                            "type": "object",
                        },
                        "type": "array",
                    },
                },
            ],
        },
        "id": "knowledge-pro-base::2e5c77da-edd7-4f1a-9407-93cd3dcab7a5",
    }

    # Validate the example configuration against the schema
    er_msgs = [
        f"Parameter: {er.json_path}, Reason: {er.message}"
        for er in list(
            jsonschema.Draft7Validator(knowledge_pro_schema).iter_errors(node_body)
        )
    ]
    errs = ";".join(er_msgs)
    print(errs)
