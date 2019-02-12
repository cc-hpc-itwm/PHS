def set_default_value_to_optional_key(key, value, dict):
    if key not in dict:
        dict[key] = value
    return dict[key]


def print_section(header):
    print('{:=^100}' .format(''))
    print('{:=^100}' .format(' ' + header + ' '))
    print('{:=^100}' .format(''))


def print_subsection(header):
    print('{:-^100}' .format(''))
    print('{:-^100}' .format(' ' + header + ' '))
    print('{:-^100}' .format(''))
