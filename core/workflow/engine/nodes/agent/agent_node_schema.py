"""JSON schema definitions for agent node configuration validation.

This module contains the JSON schema used to validate agent node configurations,
including input/output definitions, node parameters, and plugin configurations.
"""

from workflow.utils.json_schema.json_schema_cn import CNValidator

# JSON schema for validating agent node configurations
agent_node_schemas = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": ["id", "data"],
    "properties": {
        "id": {"type": "string", "pattern": "^agent::[0-9a-zA-Z-]+"},
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
                        "appId",
                        "apiKey",
                        "apiSecret",
                        "modelConfig",
                        "instruction",
                        "plugin",
                        "maxLoopCount",
                    ],
                    "properties": {
                        "appId": {"type": "string"},
                        "apiKey": {"type": "string"},
                        "apiSecret": {"type": "string"},
                        "uid": {"type": "string"},
                        "modelConfig": {
                            "type": "object",
                            "required": ["domain", "api", "agentStrategy"],
                            "properties": {
                                "domain": {"type": "string"},
                                "api": {"type": "string"},
                                "agentStrategy": {"type": "integer"},
                            },
                        },
                        "metaData": {
                            "type": "object",
                            "required": [],
                            "properties": {"caller": {"type": "string"}},
                        },
                        "instruction": {
                            "type": "object",
                            "required": ["query", "reasoning", "answer"],
                            "properties": {
                                "reasoning": {"type": "string"},
                                "answer": {"type": "string"},
                                "query": {"type": "string"},
                            },
                        },
                        "plugin": {
                            "type": "object",
                            "required": [
                                "mcpServerIds",
                                "mcpServerUrls",
                                "tools",
                                "workflowIds",
                            ],
                            "properties": {
                                "mcpServerIds": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "mcpServerUrls": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "tools": {
                                    "type": "array",
                                    "items": {
                                        "anyOf": [
                                            {"type": "string"},
                                            {
                                                "type": "object",
                                                "required": ["tool_id", "version"],
                                                "properties": {
                                                    "tool_id": {"type": "string"},
                                                    "version": {"type": "string"},
                                                },
                                            },
                                        ]
                                    },
                                },
                                "workflowIds": {
                                    "type": "array",
                                    "items": {"type": "string"},
                                },
                                "knowledge": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "name": {
                                                "type": "string",
                                                "minLength": 1,
                                                "maxLength": 128,
                                            },
                                            "description": {
                                                "type": "string",
                                                "minLength": 0,
                                                "maxLength": 1024,
                                            },
                                            "topK": {
                                                "type": "integer",
                                                "minimum": 1,
                                                "maximum": 5,
                                            },
                                            "match": {
                                                "type": "object",
                                                "properties": {
                                                    "repoIds": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "string",
                                                            "minLength": 1,
                                                        },
                                                        "minItems": 1,
                                                    },
                                                    "docIds": {
                                                        "type": "array",
                                                        "items": {
                                                            "type": "string",
                                                            "minLength": 1,
                                                        },
                                                    },
                                                },
                                                "required": ["repoIds"],
                                            },
                                            "repoType": {
                                                "type": "integer",
                                                "enum": [1, 2],
                                            },
                                        },
                                        "required": [
                                            "name",
                                            "description",
                                            "topK",
                                            "repoType",
                                            "match",
                                        ],
                                        "allOf": [
                                            {
                                                "if": {
                                                    "properties": {
                                                        "repoType": {"const": 2}
                                                    }
                                                },
                                                "then": {
                                                    "required": ["match"],
                                                    "properties": {
                                                        "match": {
                                                            "type": "object",
                                                            "properties": {
                                                                "docIds": {
                                                                    "type": "array",
                                                                    "items": {
                                                                        "type": "string",
                                                                        "minLength": 1,
                                                                    },
                                                                    "minItems": 1,
                                                                }
                                                            },
                                                            "required": ["docIds"],
                                                        }
                                                    },
                                                },
                                            }
                                        ],
                                    },
                                },
                            },
                        },
                        "maxLoopCount": {"type": "integer"},
                        "stream": {"type": "boolean"},
                        "source": {"type": "string", "enum": ["xinghuo", "openai"]},
                    },
                },
            },
        },
    },
}

if __name__ == "__main__":
    # Example agent node configuration for schema validation testing
    node_body = {
        "id": "agent::db379de3-dc37-4bf6-a47f-103a1375a64f",
        "data": {
            "nodeMeta": {"nodeType": "Agent节点", "aliasName": "智能体节点"},
            "inputs": [
                {
                    "name": "input",
                    "schema": {
                        "type": "string",
                        "value": {
                            "content": {
                                "id": "5eaf3132-a1d5-4758-a3ef-f39ccbdc117f",
                                "nodeId": "node-start::8e305103-f599-4321-abb0-5fb8c2d2d948",
                                "name": "AGENT_USER_INPUT",
                            },
                            "type": "ref",
                        },
                    },
                }
            ],
            "outputs": [
                {"name": "output", "schema": {"type": "string", "description": ""}}
            ],
            "nodeParam": {
                "appId": "4eea9****",
                "apiKey": "",
                "apiSecret": "",
                "uid": "6dc7f79bcad0476a8be9f0799f7e5e1c",
                "modelConfig": {
                    "domain": "xdeepseekr1",
                    "api": "https://xxx.com/v1",
                    "agentStrategy": 1,
                },
                "instruction": {
                    "reasoning": "如果xx，调用xxx",
                    "answer": "按照如下格式生成回答:\nxxx",
                    "query": "今天合肥天气怎么样？",
                },
                "plugin": {
                    "tools": ["tool@123456"],
                    "mcpServerIds": ["id1"],
                    "mcpServerUrls": ["url1"],
                    "workflowIds": ["id1"],
                    "knowledge": [
                        {
                            "name": "test2",
                            "description": "",
                            "topK": 3,
                            "match": {
                                "repoIds": ["9e69b8c0840a4f788a21775283acdf53"],
                                "docIds": ["1"],
                            },
                            "ragType": 1,
                        },
                        {
                            "name": "test",
                            "description": "",
                            "topK": 3,
                            "match": {"repoIds": ["c822d34918404415b40cefefff0d3237"]},
                            "repoType": 1,
                        },
                    ],
                },
                "stream": True,
                "maxLoopCount": 20,
                "metaData": {"caller": "workflow-agent-node"},
            },
        },
    }

    # Validate the example configuration against the schema
    er_msgs = [
        f"Field: {er['schema_path']}, Error: {er['message']}"
        for er in CNValidator(agent_node_schemas).validate(node_body)
    ]
    errs = ";".join(er_msgs)
    print(errs)
