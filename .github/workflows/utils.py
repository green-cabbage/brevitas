from functools import reduce
from string import Template
from textwrap import indent
from collections import OrderedDict as od

import yaml


NIX_NEWLINE = '\n'
# whitespaces to indent generated portions of output yaml
STEP_INDENT = 4
MATRIX_INDENT = 8
EXCLUDE_INDENT = 10
RELATIVE_INDENT = 2


class CustomTemplate(Template):
    delimiter = '&'


class Action:

    def __init__(self, name, exclude_list, matrix, step_list):
        self.name = name
        self.exclude_list = exclude_list
        self.matrix = matrix
        self.step_list = step_list

    @staticmethod
    def list_of_dicts_str(list_of_dicts, quote_val, indent_first):
        repr = ''
        for e in list_of_dicts:
            repr += Action.dict_str(e, quote_val, indent_first)
        return repr

    @staticmethod
    def dict_str(d, quote_val, indent_first):
        first_line_prefix = '- ' if indent_first else ''
        repr = first_line_prefix
        for name, val in d.items():
            if quote_val:
                repr += f"{name}: '{val}'" + NIX_NEWLINE
            else:
                repr += f"{name}: {val}" + NIX_NEWLINE
        if indent_first:
            repr = indent(
                repr, RELATIVE_INDENT * ' ', predicate=lambda line: not first_line_prefix in line)
        repr += NIX_NEWLINE
        return repr

    def gen_yaml(self, base_template_path, output_path):
        d = {}
        d['name'] = self.name
        d['matrix'] = indent(
            Action.dict_str(self.matrix, False, False), MATRIX_INDENT * ' ')
        d['steps'] = indent(
            Action.list_of_dicts_str(self.step_list, False, True), STEP_INDENT * ' ')
        if self.exclude_list:
            d['exclude'] = indent('exclude:\n', MATRIX_INDENT * ' ') + indent(
                Action.list_of_dicts_str(self.exclude_list, True, True), EXCLUDE_INDENT * ' ')
        else:
            d['exclude'] = ''
        template = CustomTemplate(open(base_template_path).read())
        generated_file = template.substitute(d)
        yaml.safe_load(generated_file)  # validate the generated yaml
        with open(output_path, 'w', newline=NIX_NEWLINE) as f:
            f.write(generated_file)


def combine_od_list(od_list):
    return od(reduce(lambda l1, l2: l1 + l2, list(map(lambda d: list(d.items()), od_list))))