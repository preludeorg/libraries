import json
import uuid


def check_if_string_is_uuid(string):
    try:
        uuid.UUID(string)
        return True
    except ValueError:
        return False


class SortedListEncoder(json.JSONEncoder):
    def encode(self, obj):
        def get_key(item):
            if isinstance(item, dict):
                k = get_key(sorted(item.keys())[0])
                return k
            else:
                return str(item)

        def sort_lists(item):
            if isinstance(item, list):
                return sorted(
                    (sort_lists(i) for i in item),
                    key=lambda nm: (
                        nm[get_key(nm)] if isinstance(nm, dict) else get_key(nm)
                    ),
                )
            elif isinstance(item, dict):
                return {k: sort_lists(v) for k, v in item.items()}
            else:
                return item

        return super(SortedListEncoder, self).encode(sort_lists(obj))


def check_dict_items(expected, actual):
    def _check_ordered_dict_items(expected, actual):
        diffs = []
        for k, v in expected.items():
            if isinstance(v, dict):
                diffs.extend(_check_ordered_dict_items(v, actual[k]))
                continue
            if isinstance(v, list):
                if v and isinstance(v[0], dict):
                    for i in range(len(v)):
                        if i < len(actual[k]):
                            diffs.extend(_check_ordered_dict_items(v[i], actual[k][i]))
                        else:
                            diffs.append(f"[{k}] expected: {v}  actual: None")
                    continue
                if sorted(v) != sorted(actual[k]):
                    diffs.append(f"[{k}] expected: {v}  actual: {actual[k]}")
                    continue
            if v != actual[k]:
                diffs.append(f"[{k}] expected: {v}  actual: {actual[k]}")
        return diffs

    expected = json.loads(
        json.dumps(expected, sort_keys=True, default=str, cls=SortedListEncoder)
    )
    actual = json.loads(
        json.dumps(actual, sort_keys=True, default=str, cls=SortedListEncoder)
    )
    return _check_ordered_dict_items(expected, actual)
