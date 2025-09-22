"""
Node Schema Registry Module

This module provides a centralized registry for all workflow node type schemas.
It serves as a validation registry that maps node type identifiers to their
corresponding JSON schemas for input validation and configuration verification.

The registry includes JSON schemas for all supported node types in the workflow
engine, enabling runtime validation of node configurations and parameters.
"""

from workflow.engine.nodes.agent.agent_node_schema import agent_node_schemas
from workflow.engine.nodes.code.code_schema import code_schema
from workflow.engine.nodes.decision.spark_decision_schema import spark_decision_schema
from workflow.engine.nodes.end.end_schema import end_schema
from workflow.engine.nodes.flow.flow_node_schema import flow_node_schemas
from workflow.engine.nodes.global_variables.global_variables_schema import (
    variables_schemas,
)
from workflow.engine.nodes.if_else.if_else_schema import if_else_schema
from workflow.engine.nodes.iteration.iteration_node_schema import (
    iteration_end_schema,
    iteration_schema,
    iteration_start_schema,
)
from workflow.engine.nodes.knowledge.knowledge_schema import knowledge_schema
from workflow.engine.nodes.knowledge_pro.knowledge_pro_schema import (
    knowledge_pro_schema,
)
from workflow.engine.nodes.llm.spark_llm_schema import spark_llm_schema
from workflow.engine.nodes.message.message_schema import message_schema
from workflow.engine.nodes.params_extractor.pe_schema import pe_schema
from workflow.engine.nodes.pgsql.pgsql_schema import pgsql_schema
from workflow.engine.nodes.plugin_tool.plugin_schema import plugin_schema
from workflow.engine.nodes.question_answer.question_answer_node_schema import (
    question_answer_schema,
)
from workflow.engine.nodes.start.spark_start_schema import spark_start_schema
from workflow.engine.nodes.text_joiner.text_joiner_shema import text_joiner_schema

# Registry mapping node types to their corresponding JSON schemas
# This dictionary provides schema validation for all supported node types
# Each schema defines the expected structure, types, and constraints for node configuration
node_schema = {
    "ifly-code": code_schema,  # Schema for code execution node configuration
    "node-start": spark_start_schema,  # Schema for workflow start node configuration
    "node-end": end_schema,  # Schema for workflow end node configuration
    "plugin": plugin_schema,  # Schema for plugin tool node configuration
    "knowledge-base": knowledge_schema,  # Schema for knowledge base node configuration
    "knowledge-pro-base": knowledge_pro_schema,  # Schema for professional knowledge base node configuration
    "spark-llm": spark_llm_schema,  # Schema for Spark LLM node configuration
    "decision-making": spark_decision_schema,  # Schema for decision making node configuration
    "if-else": if_else_schema,  # Schema for conditional branching node configuration
    "message": message_schema,  # Schema for message output node configuration
    "extractor-parameter": pe_schema,  # Schema for parameter extraction node configuration
    "iteration": iteration_schema,  # Schema for iteration node configuration
    "iteration-node-start": iteration_start_schema,  # Schema for iteration start node configuration
    "iteration-node-end": iteration_end_schema,  # Schema for iteration end node configuration
    "text-joiner": text_joiner_schema,  # Schema for text joining node configuration
    "node-variable": variables_schemas,  # Schema for global variables node configuration
    "flow": flow_node_schemas,  # Schema for sub-flow node configuration
    "agent": agent_node_schemas,  # Schema for agent node configuration
    "database": pgsql_schema,  # Schema for PostgreSQL database node configuration
    "question-answer": question_answer_schema,  # Schema for question-answer node configuration
}
