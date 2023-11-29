import enum
from deepdiff import DeepDiff


def get_formatted_changes_string(list1: list, list2: list) -> str:
    diff = DeepDiff(list1, list2)
    values_changed = diff.get('values_changed', {})
    return str({"resource": next(iter((values_changed.values())))})


class OperationTypeEnum(enum.Enum):
    INSERT = "INSERT"
    UPDATE = "UPDATE"
