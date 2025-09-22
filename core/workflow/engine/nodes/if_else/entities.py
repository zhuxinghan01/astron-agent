from typing import List, Literal, Union

from pydantic import BaseModel


class IfElseNodeData(BaseModel):
    """
    Data structure for storing information of a branch block in an if-else node.

    This class represents a single branch within an if-else conditional node,
    containing the conditions to be evaluated and the logical operators
    that connect them.
    """

    class Condition(BaseModel):
        """
        Represents a single condition within a branch.

        :param leftVarIndex: Index of the left operand variable in the input identifier
        :param rightVarIndex: Index of the right operand variable in the input identifier
        :param compareOperator: Comparison operator to be used for evaluation
        """

        leftVarIndex: str
        rightVarIndex: str
        """Comparison operator for evaluating the condition"""
        compareOperator: Literal[
            # String or array comparison operators
            "contains",
            "not_contains",
            "start_with",
            "end_with",
            "is",
            "is_not",
            "empty",
            "not_empty",
            # Numeric comparison operators
            "eq",
            "ne",
            "gt",
            "lt",
            "ge",
            "le",
            "null",
            "not_null",
        ]

    # All condition statements in the node
    conditions: Union[List[Condition], List[None]]

    # Logical relationship between condition statements.
    # Conditions are connected either by "and" or "or", no nested logic exists.
    logical_operator: Literal["and", "or"] = "and"

    # Priority level of the current branch
    branch_level: int

    # Unique identifier for the current branch
    branch_id: str
