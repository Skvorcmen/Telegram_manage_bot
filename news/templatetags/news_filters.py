from django import template

register = template.Library()

@register.filter
def count_published(posts):
    """Считает опубликованные новости."""
    count = 0
    for post in posts:
        if post.is_published:
            count += 1
    return count

@register.filter
def count_drafts(posts):
    """Считает черновики."""
    count = 0
    for post in posts:
        if not post.is_published:
            count += 1
    return count
