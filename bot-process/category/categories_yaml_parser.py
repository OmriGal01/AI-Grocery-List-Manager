import yaml
from pathlib import Path

CATEGORIES_CONFIG_PATH = Path(__file__).resolve().parent / "categories_config.yaml"

def normalize_name(name: str) -> str:
    return name.strip().lower()

unnormalized_lang_item_to_category = yaml.safe_load(CATEGORIES_CONFIG_PATH.read_text(encoding='utf-8'))
normalized_lang_item_to_category = {}
for language, language_data in unnormalized_lang_item_to_category.items():
    specific_lang_to_category = {}
    for item_name, category in language_data.items():
        specific_lang_to_category[normalize_name(item_name)] = normalize_name(category)
    normalized_lang_item_to_category[language] = specific_lang_to_category

LANG_ITEM_TO_CATEGORY = normalized_lang_item_to_category
