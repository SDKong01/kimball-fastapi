from typing import List, Dict
from rapidfuzz import fuzz
from src.constants import SYS_METADATA_COLLECTION, DATE_COLUMN_NAME


def fuzzy_str_list_match(query: str, options: List[str], threshold: int = 70) -> float:
    return sum(
        [
            ratio
            for option in options
            if (ratio := fuzz.ratio(query, option)) > threshold
        ]
    )


def fuzzy_list_list_match(
    query: List[str], options: List[str], threshold: int = 70
) -> float:
    return sum(
        [
            ratio
            for q in query
            if (ratio := fuzzy_str_list_match(q, options, threshold)) > threshold
        ]
    )


def parse_fields_dict(
    fields_human: Dict[str, List[str]], fields_dataset: Dict[str, List[str]]
) -> Dict[str, str]:
    fields_map = {}

    for key, value in fields_human.items():
        if value == DATE_COLUMN_NAME:
            fields_map[key] = DATE_COLUMN_NAME
            continue

        field_score = 0
        field_name = ""
        for f_key, f_value in fields_dataset.items():
            new_score = fuzzy_list_list_match(f_value, value)
            if new_score > field_score:
                field_score = new_score
                field_name = f_key
        fields_map[key] = field_name

    return fields_map
