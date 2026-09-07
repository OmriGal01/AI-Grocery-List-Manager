import rapidfuzz.process
from category.categories_yaml_parser import LANG_ITEM_TO_CATEGORY, normalize_name

THRESHOLD = 80

def find_category(item_name: str, language: str | None = None) -> str | None:
    item_names_to_category_map = LANG_ITEM_TO_CATEGORY.get(language, {})
    if not item_names_to_category_map:
        for lang_specific_map in LANG_ITEM_TO_CATEGORY.values():
            item_names_to_category_map |= lang_specific_map

    normalized_item_name = normalize_name(item_name)
    item_candidates = item_names_to_category_map.keys()
    item_match = rapidfuzz.process.extractOne(normalized_item_name, item_candidates, scorer=rapidfuzz.fuzz.ratio, score_cutoff=THRESHOLD)
    if not item_match:
        return None

    return item_names_to_category_map[item_match[0]]