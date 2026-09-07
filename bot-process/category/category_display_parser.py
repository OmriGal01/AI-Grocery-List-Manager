from pathlib import Path
from collections import defaultdict
from category.yaml_parsing_utils import get_raw_yaml_dict, normalize_name

CATEGORIES_DISPLAY_CONFIG_PATH = Path(__file__).resolve().parent / "category_display_config.yaml"

def _build_category_to_emoji_map() -> defaultdict[str, str]:
    unnormalized_category_displays = get_raw_yaml_dict(CATEGORIES_DISPLAY_CONFIG_PATH)
    unknown_emoji = unnormalized_category_displays['unknown_emoji']
    category_to_emoji = defaultdict(lambda: unknown_emoji)
    for category in unnormalized_category_displays['categories']:
        emoji = category['emoji']
        for category_name in category['names']:
            category_to_emoji[normalize_name(category_name)] = emoji
    return category_to_emoji

def _build_category_to_order_map() -> defaultdict[str, int]:
    unnormalized_category_displays = get_raw_yaml_dict(CATEGORIES_DISPLAY_CONFIG_PATH)
    num_categories = len(unnormalized_category_displays['categories'])
    category_to_order = defaultdict(lambda: num_categories)
    for index, category in enumerate(unnormalized_category_displays['categories']):
        for category_name in category['names']:
            category_to_order[normalize_name(category_name)] = index
    return category_to_order

CATEGORY_TO_EMOJI = _build_category_to_emoji_map()
CATEGORY_TO_ORDER = _build_category_to_order_map()