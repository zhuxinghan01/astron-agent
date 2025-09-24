import json
import re
from typing import Any, Union

from workflow.engine.entities.variable_pool import VariablePool
from workflow.engine.nodes.util.string_parse import get_need_find_var_name, parse_prompt
from workflow.exception.e import CustomException
from workflow.exception.errors.err_code import CodeEnum
from workflow.extensions.otlp.trace.span import Span


# Find and replace variables in text (deprecated method)
def replace_variables_deprecated(text: str, replacements: dict) -> str:
    """
    Replace variables in text using regex pattern matching (deprecated).

    This function uses regex to find and replace variables in the format {{variable_name}}
    with their corresponding values from the replacements dictionary.

    :param text: Text containing variables to be replaced
    :param replacements: Dictionary mapping variable names to their values
    :return: Text with variables replaced
    """

    def replacer(match: re.Match[str]) -> str:
        # Extract content between {{}}
        key = match.group(1)
        # Return replacement value if key exists in replacements dict, otherwise return original key
        return replacements.get(key, f"{{{{{key}}}}}")

    # Define regex pattern to match content wrapped in {{}}
    pattern = r"\{\{(.*?)\}\}"
    # Perform replacement
    return re.sub(pattern, replacer, text)


def replace_variables(prompt_template: str, replacements: dict) -> str:
    """
    Replace variables in prompt template using template unit parsing.

    This function parses the prompt template into template units and replaces
    variables with their corresponding values from the replacements dictionary.

    :param prompt_template: Template string containing variables
    :param replacements: Dictionary mapping variable names to their values
    :return: Template with variables replaced
    """
    template_unit_list = parse_prompt(prompt_template)
    ans = ""
    for index, template_unit in enumerate(template_unit_list):
        if template_unit.key_type == 1:
            ans += replacements.get(
                template_unit.key, "{{" + template_unit.key + "}}"
            )  # Keep original variable format if not found in replacements
        else:
            ans += template_unit.key
    return ans


def process_array(name: str) -> str:
    """
    Extract array name from array access expression.

    :param name: Array access expression like 'array_name[0]'
    :return: Array name without index brackets
    """
    bracket_left_index = name.find("[")
    array_name = name[0:bracket_left_index]
    return array_name


def parse_nested_array(arr: list, index_str: str) -> Union[Any, None]:
    """
    Parse nested array values based on string notation (e.g., 'arr_arr_input[0][0]').

    This function extracts values from nested arrays using string-based index expressions.

    :param arr: Target nested array
    :param index_str: String representation of index expression (e.g., 'arr_arr_input[0][0]')
    :return: Parsed value from the nested array
    """
    import re

    # Extract indices from array expression, e.g., 'arr_arr_input[0][0]' -> ['0', '0']
    index_list = re.findall(r"\[(\d+)\]", index_str)
    # Convert indices to integer list
    indices = [int(i) for i in index_list]
    # Iteratively parse array values using extracted indices
    result = arr
    for idx in indices:
        result = result[idx]
    return result


def process_prompt(
    node_id: str, key_name: str, variable_pool: VariablePool, span: Span
) -> Union[Any | None]:
    """
    Process various types of variables including complex nested structures.

    This function handles variable names with complex access patterns such as:
    - valid.match
    - array[0]
    - another.valid[1].match
    - input[0].xx1[0].xxx1[0]

    :param node_id: ID of the current node
    :param key_name: Variable name with potential nested access
    :param variable_pool: Pool containing variables and their values
    :param span: Tracing span for monitoring
    :return: Resolved variable value or None if not found
    :raises: CustomException if variable parsing fails
    """

    try:
        key_name_parts = key_name.split(".")
        last_part: Any = None
        for index, cur_part_key_name in enumerate(key_name_parts):
            arr_name = (
                process_array(cur_part_key_name)
                if "[" in cur_part_key_name
                else cur_part_key_name
            )
            try:
                last_part = (
                    variable_pool.get_variable(
                        node_id=node_id, key_name=arr_name, span=span
                    )
                    if index == 0
                    else last_part.get(arr_name)
                )
            except Exception:
                # User's key_name is incorrect and not found in variable pool
                return key_name
            last_part = (
                parse_nested_array(last_part, cur_part_key_name)
                if "[" in cur_part_key_name
                else last_part
            )
        return last_part
    except Exception as e:
        raise CustomException(
            err_code=CodeEnum.VARIABLE_PARSE_ERROR,
            err_msg=f"Variable name: {key_name} parsing failed, reason: {str(e)}",
        ) from e


def prompt_template_replace(
    input_identifier: list,
    _prompt_template: str,
    node_id: str,
    variable_pool: VariablePool,
    span_context: Span,
) -> str:
    """
    Replace variables in prompt template with their actual values.

    This function processes a prompt template by finding all variables,
    resolving their values from the variable pool, and replacing them
    in the template string.

    :param input_identifier: List of valid input variable identifiers
    :param _prompt_template: Template string containing variables
    :param node_id: ID of the current node
    :param variable_pool: Pool containing variables and their values
    :param span_context: Tracing span for monitoring
    :return: Template with variables replaced by their values
    """
    need_find_var_name = get_need_find_var_name(
        node_id=node_id,
        variable_pool=variable_pool,
        prompt_template=_prompt_template,
        span_context=span_context,
    )
    replacements = {}
    for var_name in need_find_var_name:
        var_name_list = re.split(r"[\[.\]]", var_name)
        if var_name_list[0].strip() in input_identifier:
            replacements.update(
                {
                    var_name: process_prompt(
                        node_id=node_id,
                        key_name=var_name,
                        variable_pool=variable_pool,
                        span=span_context,
                    )
                }
            )

    replacements_str = {}
    for key, value in replacements.items():
        try:
            if not isinstance(value, str):
                # Convert non-string values to JSON format for template replacement
                value = json.dumps(value, ensure_ascii=False)
        except Exception:
            value = ""
        replacements_str[key] = value

    # Replace variables in template with resolved values
    _prompt_template = replace_variables(_prompt_template, replacements_str)
    return _prompt_template
