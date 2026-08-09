import nh3

_ALLOWED_TAGS = {"p", "br", "b", "strong", "i", "em", "u", "ul", "ol", "li", "span"}


def sanitize_rich_text(raw_html: str | None) -> str | None:
    """Ijobiy/salbiy fazilatlar kabi rich-text maydonlarini bazaga yozishdan oldin tozalaydi."""
    if raw_html is None:
        return None
    return nh3.clean(raw_html, tags=_ALLOWED_TAGS)
