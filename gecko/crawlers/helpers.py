from bs4 import Tag


def has_class(tag: Tag, klass: str):
    if not isinstance(tag, Tag):
        return False
    return tag.has_attr('class') and klass in tag.get('class')
