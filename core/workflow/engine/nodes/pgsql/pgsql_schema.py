import jsonschema  # type: ignore

# JSON Schema definition for PostgreSQL node configuration validation
pgsql_schema = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        # Node identifier with database prefix pattern
        "id": {"type": "string", "pattern": "^database::[0-9a-zA-Z-]+"},
        # Node data configuration
        "data": {
            "type": "object",
            "required": ["nodeMeta", "inputs", "outputs", "nodeParam"],
            "properties": {
                # Node metadata information
                "nodeMeta": {
                    "type": "object",
                    "properties": {
                        "nodeType": {"type": "string"},
                        "aliasName": {"type": "string"},
                    },
                },
                # Input parameter definitions
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
                # Output parameter definitions
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
                                            "null",
                                        ],
                                    }
                                },
                            },
                        },
                    },
                },
                # Node-specific parameters for PostgreSQL operations
                "nodeParam": {
                    "type": "object",
                    "required": ["appId", "apiKey", "uid", "dbId", "mode"],
                    "properties": {
                        # Application identifier for authentication
                        "appId": {"type": "string", "minLength": 1, "maxLength": 10},
                        # API key for service authentication
                        "apiKey": {"type": "string", "minLength": 1},
                        # User identifier for the operation
                        "uid": {
                            "type": "string",
                            "maxLength": 64,
                            "pattern": "^[0-9a-zA-Z]+",
                        },
                        # Database identifier
                        "dbId": {"type": "integer"},
                        # Target table name for operations
                        "tableName": {"type": "string"},
                        # Workspace or space identifier
                        "spaceId": {"type": ["integer", "string"]},
                        # Custom SQL statement for CUSTOM mode
                        "sql": {"type": "string", "minLength": 1},
                        # Operation mode: 0=CUSTOM, 1=ADD, 2=UPDATE, 3=SEARCH, 4=DELETE
                        "mode": {"type": "integer", "enum": [0, 1, 2, 3, 4]},
                        # Query conditions for WHERE clauses
                        "cases": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["logicalOperator", "conditions"],
                                "properties": {
                                    "logicalOperator": {
                                        "type": "string",
                                        "enum": ["and", "or"],
                                    },
                                    "conditions": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "required": [
                                                "fieldName",
                                                "varIndex",
                                                "selectCondition",
                                            ],
                                            "properties": {
                                                "fieldName": {
                                                    "type": "string",
                                                    "minLength": 1,
                                                },
                                                "varIndex": {
                                                    "type": "string",
                                                    "minLength": 1,
                                                },
                                                "selectCondition": {
                                                    "type": "string",
                                                    "enum": [
                                                        "=",
                                                        "!=",
                                                        "like",
                                                        "not like",
                                                        "in",
                                                        "not in",
                                                        "null",
                                                        "not null",
                                                        "<",
                                                        "<=",
                                                        ">",
                                                        ">=",
                                                    ],
                                                },
                                                "fieldType": {
                                                    "type": "string",
                                                },
                                            },
                                        },
                                    },
                                },
                            },
                        },
                        # Column names for SELECT/UPDATE operations
                        "assignmentList": {
                            "type": "array",
                            "items": {"type": "string", "minLength": 1},
                        },
                        # ORDER BY clause configuration
                        "orderData": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "required": ["fieldName", "order"],
                                "properties": {
                                    "fieldName": {"type": "string", "minLength": 1},
                                    "order": {
                                        "type": "string",
                                        "enum": ["asc", "desc"],
                                    },
                                },
                            },
                        },
                        # LIMIT clause value for SELECT operations
                        "limit": {"type": "integer", "minimum": 0},
                    },
                },
            },
        },
    },
}

if __name__ == "__main__":
    # Test schema validation with sample node configuration
    node_body = {
        "id": "pgsql-base::831c1984-9de2-4b55-9e0d-d23a87282539",
        "data": {
            "nodeMeta": {"nodeType": "数据库节点", "aliasName": "add节点"},
            "inputs": [
                {
                    "name": "book_name",
                    "id": "book_name_uuid",
                    "schema": {
                        "type": "string",
                        "value": {
                            "content": {
                                "id": "5eaf3132-a1d5-4758-a3ef-f39ccbdc117f",
                                "nodeId": "ifly-code::0823bdf8-baa1-43c6-9dab-270c32e534f0",
                                "name": "key0",
                            },
                            "type": "ref",
                        },
                    },
                },
                {
                    "name": "note",
                    "id": "note_uuid",
                    "schema": {
                        "type": "string",
                        "value": {
                            "content": {
                                "id": "5eaf3132-a1d5-4758-a3ef-f39ccbdc117f",
                                "nodeId": "ifly-code::0823bdf8-baa1-43c6-9dab-270c32e534f0",
                                "name": "key0",
                            },
                            "type": "ref",
                        },
                    },
                },
            ],
            "outputs": [
                {
                    "name": "outputList",
                    "schema": {"type": "array", "items": {"type": "object"}},
                },
                {
                    "name": "rowNum",
                    "schema": {
                        "type": "integer",
                    },
                },
            ],
            "nodeParam": {
                "appId": "appId",
                "apiKey": "apiKey",
                "apiSecret": "apiSecret",
                "uid": "uid",
                "dbId": 123,
                "tableName": "tableName",
                "mode": 1,
                "cases": [
                    {
                        "logicalOperator": "and",
                        "conditions": [
                            {
                                "fieldName": "fieldName1",
                                "varIndex": "varIndex1",
                                "selectCondition": "=",
                            },
                            {
                                "fieldName": "fieldName2",
                                "varIndex": "varIndex2",
                                "selectCondition": "!=",
                            },
                        ],
                    },
                    {
                        "logicalOperator": "or",
                        "conditions": [
                            {
                                "fieldName": "fieldName1",
                                "varIndex": "varIndex1",
                                "selectCondition": "=",
                            },
                            {
                                "fieldName": "fieldName2",
                                "varIndex": "varIndex2",
                                "selectCondition": "!=",
                            },
                        ],
                    },
                ],
                "assignmentList": ["item"],
                "orderData": [
                    {
                        "fieldName": "fieldName1",
                        "order": "asc",
                    },
                    {
                        "fieldName": "fieldName2",
                        "order": "desc",
                    },
                ],
                "limit": 1,
            },
        },
    }
    # Validate the sample configuration against the schema
    res = list(jsonschema.Draft7Validator(pgsql_schema).iter_errors(node_body))
    print(res)
