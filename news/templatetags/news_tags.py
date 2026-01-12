from django import template

register = template.Library()

@register.simple_tag
def count_published(posts):
    """Считает опубликованные новости."""
    return sum(1 for post in posts if post.is_published)

@register.simple_tag
def count_drafts(posts):
    """Считает черновики."""
    return sum(1 for post in posts if not post.is_published)
