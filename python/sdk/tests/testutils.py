import uuid


def check_if_string_is_uuid(string):
    try:
        uuid.UUID(string)
        return True
    except ValueError:
        return False


def check_dict_items(expected, actual):
    diffs = []
    for k, v in expected.items():
        if isinstance(v, dict):
            diffs.extend(check_dict_items(v, actual[k]))
            continue
        if isinstance(v, list):
            if v and isinstance(v[0], dict):
                for i in range(len(v)):
                    if i < len(actual[k]):
                        diffs.extend(check_dict_items(v[i], actual[k][i]))
                    else:
                        diffs.append(f'[{k}] expected: {v}  actual: None')
                continue
            if sorted(v) != sorted(actual[k]):
                diffs.append(f'[{k}] expected: {v}  actual: {actual[k]}')
                continue
        if v != actual[k]:
            diffs.append(f'[{k}] expected: {v}  actual: {actual[k]}')
    return diffs