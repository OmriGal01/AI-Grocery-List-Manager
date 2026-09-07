from pathlib import Path
from category.yaml_parsing_utils import get_raw_yaml_dict, normalize_name

CATEGORIES_CONFIG_PATH = Path(__file__).resolve().parent / "categories_config.yaml"
unnormalized_lang_item_to_category = get_raw_yaml_dict(CATEGORIES_CONFIG_PATH)

def _build_lang_item_to_category_map() -> dict[str, str]:
    normalized_lang_item_to_category = {}
    for language, language_data in unnormalized_lang_item_to_category.items():
        specific_lang_to_category = {}
        for item_name, category in language_data.items():
            specific_lang_to_category[normalize_name(item_name)] = normalize_name(category)
        normalized_lang_item_to_category[language] = specific_lang_to_category
    return normalized_lang_item_to_category

LANG_ITEM_TO_CATEGORY = _build_lang_item_to_category_map()
