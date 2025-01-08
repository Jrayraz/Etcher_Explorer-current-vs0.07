import re
from oscan import dto
from oscan import util
from oscan.error import Error


def scan(text, pattern):
    """
    pattern is one of:
    - string;
    - list or tuple of 2-tuples (name, regex);
    - an enum of regex patterns
    """
    if isinstance(pattern, str):
        specification = [("", pattern)]
    elif isinstance(pattern, list) or isinstance(pattern, tuple):
        specification = pattern
    else:
        specification = util.create_specification(pattern)
        pattern = "|".join("(?P<{}>{})".format(name, regex)
                           for name, regex in specification)
    for match_obj in re.finditer(pattern, text, re.MULTILINE):
        name, groups_list, groups_dict = util.interpret_match(match_obj)
        yield dto.Token(name, groups_list, groups_dict)


def match(text, pattern):
    """
    pattern is one of:
    - string;
    - list or tuple of 2-tuples (name, regex);
    - an enum of regex patterns
    """
    if isinstance(pattern, str):
        specification = [("", pattern)]
    elif isinstance(pattern, list) or isinstance(pattern, tuple):
        specification = pattern
    else:
        specification = util.create_specification(pattern)
    for name, regex in specification:
        match_obj = re.fullmatch(regex, text)
        if not match_obj:
            continue
        _, groups_list, groups_dict = util.interpret_match(match_obj)
        return dto.Token(name, groups_list, groups_dict)
    return None
