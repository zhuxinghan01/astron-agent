import re

from workflow.engine.entities.variable_pool import VariablePool
from workflow.extensions.otlp.trace.span import Span


class TemplateUnitObj:
    """
    Object representing a unit in a template string.

    This class represents either a constant string or a variable reference
    within a template, along with metadata about its type and dependencies.

    :param key: The value for constants or the name for variables
    :param key_type: Type indicator (0=constant, 1=variable)
    :param is_end: Whether this is the final part of the template
    :param dep_node_id: ID of the referenced node when this is a variable
    :param ref_var_name: Original name of the referenced variable
    """

    key: str  # Value for constants or name for variables
    key_type: int  # 0: constant; 1: variable
    is_end: bool = False  # Whether this is the final output part of the template
    dep_node_id = ""  # ID of the referenced node when this is a variable

    def __init__(self) -> None:
        self.key = ""
        # Original name of the referenced key
        self.ref_var_name = ""
        self.key_type = 0
        self.is_end = False
        self.dep_node_id = ""

    @classmethod
    def generate_const_unit(cls, key: str) -> "TemplateUnitObj":
        """
        Generate a template unit object for a constant string.

        :param key: The constant string value
        :return: TemplateUnitObj representing a constant
        """
        instance = cls()
        instance.key = key
        instance.key_type = 0
        instance.is_end = False
        return instance

    @classmethod
    def generate_var_unit(cls, key: str) -> "TemplateUnitObj":
        """
        Generate a template unit object for a variable reference.

        :param key: The variable name
        :return: TemplateUnitObj representing a variable
        """
        instance = cls()
        instance.key = key
        instance.key_type = 1
        instance.is_end = False
        instance.dep_node_id = ""
        return instance


# TODO: Code optimization needed for better performance
def parse_prompt_deprecated(template: str) -> list[TemplateUnitObj]:
    """
    Parse prompt template into template units (deprecated method).

    This function parses a template string and breaks it down into
    constant and variable units. This is a deprecated implementation
    that should be replaced with the newer parse_prompt function.

    :param template: Template string to parse
    :return: List of TemplateUnitObj representing the parsed template
    """
    template_unit_list: list[TemplateUnitObj] = []

    i = 0
    while i < len(template):
        if template[i : i + 2] == "{{":  # Start of variable section
            j = i + 2
            while j < len(template) and template[j : j + 2] != "}}":
                j += 1
            if j < len(template):  # Found closing }}, this is a complete variable
                var_name = template[i + 2 : j]
                template_unit = TemplateUnitObj.generate_var_unit(key=var_name)
                template_unit_list.append(template_unit)
                i = j + 2  # Skip }}, continue checking remaining content
            else:  # Only {{ without closing
                template_unit = TemplateUnitObj.generate_const_unit(key=template[i:])
                template_unit_list.append(template_unit)
                break  # Treat remaining part as constant, output directly
        elif template[i : i + 2] == "}}":  # Only }}, treat as constant
            template_unit = TemplateUnitObj.generate_const_unit(key=template[i:])
            template_unit_list.append(template_unit)
            break  # Remaining part is constant, output directly
        else:  # Constant part
            j = i
            while j < len(template) and template[j : j + 2] != "{{":
                j += 1
            template_unit = TemplateUnitObj.generate_const_unit(key=template[i:j])
            template_unit_list.append(template_unit)
            i = j  # Skip constant part, continue checking remaining content

    return template_unit_list


def get_need_find_var_name(
    node_id: str, variable_pool: VariablePool, prompt_template: str, span_context: Span
) -> list:
    """
    Extract variable names referenced in the prompt template.

    This function parses the prompt template and identifies all variables
    that need to be resolved from the variable pool.

    :param node_id: ID of the current node
    :param variable_pool: Pool containing variables and their values
    :param prompt_template: Template string to analyze
    :param span_context: Tracing span for monitoring
    :return: List of variable names that need to be resolved
    """
    need_find_var_name = []
    template_unit_list = parse_prompt(template=prompt_template)
    for index, template_unit in enumerate(template_unit_list):
        if template_unit.key_type == 1:
            dep_node_id = variable_pool.get_variable_ref_node_id(
                node_id, template_unit.key, span_context
            ).ref_node_id
            if dep_node_id:
                need_find_var_name.append(template_unit.key)
    return need_find_var_name


def integration_const_parts(
    template_unit_list: list[TemplateUnitObj],
) -> list[TemplateUnitObj]:
    """
    Integrate consecutive constant parts into single units.

    This function merges adjacent constant template units to optimize
    the template structure. For example:
    content_parts = ['xxxx', '}', '{{{']
    type_parts = [1, 0, 0]

    After integration:
    content_parts = ['xxxx', '}{{{']
    type_parts = [1, 0]

    :param template_unit_list: List of template units to process
    :return: List of template units with consecutive constants merged
    """
    length = len(template_unit_list)
    r = 0
    new_template_unit_list = []
    while r < length:
        cur_content = ""
        if template_unit_list[r].key_type == 1:
            new_template_unit_list.append(template_unit_list[r])
            r += 1
            continue
        while r < length and template_unit_list[r].key_type == 0:
            cur_content += template_unit_list[r].key
            r += 1
        template_unit = TemplateUnitObj.generate_const_unit(key=cur_content)
        new_template_unit_list.append(template_unit)

    return new_template_unit_list


def is_varname_valid(varname: str) -> bool:
    """
    Validate variable name according to naming rules.

    Variable naming rules:
    1. Only numbers, letters, "[", "]", ".", "_" are allowed
    2. Cannot contain "{" or "}"
    3. Must start with letters or numbers

    :param varname: Variable name to validate
    :return: True if variable name is valid, False otherwise
    """
    valid_varname_pattern = r"^[a-zA-Z0-9][a-zA-Z0-9\[\]_.]*$"
    return bool(re.match(valid_varname_pattern, varname))


def parse_prompt(template: str) -> list[TemplateUnitObj]:
    """
    Parse prompt template into template units with validation.

    This function parses a template string and breaks it down into
    constant and variable units, with proper validation of variable names.

    :param template: Template string to parse
    :return: List of TemplateUnitObj representing the parsed template
    """
    template_unit_list: list[TemplateUnitObj] = []

    # Step1 : Extract content between {{ ... }}
    braces_pattern = re.compile(r"\{\{(.*?)}}")
    raw_matches = braces_pattern.findall(template)

    # Step2: Define variable name rules
    # Single name: letters, numbers, underscores, hyphens
    name_pattern = r"[A-Za-z0-9_-]+"
    # Optional array index: multiple [numbers], allow negative numbers
    index_pattern = r"(?:\[-?\d+\])*"
    # One complete segment: name + optional index
    segment_pattern = rf"{name_pattern}{index_pattern}"
    # Multiple segments connected by dots
    variable_pattern = re.compile(rf"^{segment_pattern}(?:\.{segment_pattern})*$")

    # Step3: Filter valid variable names
    for key in raw_matches:
        if not variable_pattern.match(key):
            continue
        template_unit = TemplateUnitObj.generate_var_unit(key=key)
        template_unit_list.append(template_unit)
    return template_unit_list
