

def create_specification(pattern_enum):
    specification = list()
    for member in pattern_enum:
        cache = (member.name, member.value)
        specification.append(cache)
    return specification


def interpret_match(match_obj):
    groups_list = list()
    groups_dict = dict()
    for group in match_obj.groups():
        if group is not None:
            groups_list.append(group)
    for name, group in match_obj.groupdict().items():
        if group is not None:
            groups_dict[name] = group
    return match_obj.lastgroup, groups_list, groups_dict
