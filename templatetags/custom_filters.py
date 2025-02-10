from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_item_list(list_obj, index):
    try:
        return list_obj[int(index)]
    except (IndexError, ValueError, TypeError):
        return None
