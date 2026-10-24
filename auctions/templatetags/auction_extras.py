from django import template

register = template.Library()

# Kept next to the catalog so the categories page has a single source of truth.
EMOJI_BY_NAME = {
    "books": "📚",
    "book": "📚",
    "electronics": "💻",
    "computer": "💻",
    "computers": "💻",
    "phones": "📱",
    "phone": "📱",
    "home": "🏠",
    "furniture": "🪑",
    "fashion": "👗",
    "clothing": "👕",
    "shoes": "👟",
    "toys": "🧸",
    "games": "🎮",
    "gaming": "🎮",
    "sports": "⚽",
    "art": "🎨",
    "music": "🎵",
    "jewelry": "💎",
    "watches": "⌚",
    "collectibles": "🏺",
    "vehicles": "🚗",
    "cars": "🚗",
    "garden": "🌿",
    "kitchen": "🍳",
    "beauty": "💄",
    "pets": "🐾",
}

DEFAULT_EMOJI = "🏷️"


@register.filter
def category_emoji(name):
    """Return an emoji icon for a category name (case-insensitive, keyword match)."""
    if not name:
        return DEFAULT_EMOJI
    key = str(name).strip().lower()
    if key in EMOJI_BY_NAME:
        return EMOJI_BY_NAME[key]
    for word, emoji in EMOJI_BY_NAME.items():
        if word in key:
            return emoji
    return DEFAULT_EMOJI
