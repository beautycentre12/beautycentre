# custom_filters.py
from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """
    Multiply the value by the given argument.
    """
    try:
        return value * arg
    except (ValueError, TypeError):
        return ''

@register.filter
def sum_subtotal(value, arg):
    """
    Add the value by the given argument.
    """
    try:
        return value + arg
    except (ValueError, TypeError):
        return ''

@register.filter(name='linebreak_every_n_words')
def linebreak_every_n_words(value, n=2):
    words = value.split()
    result = []
    
    for i in range(0, len(words), n):
        result.append(' '.join(words[i:i + n]))
    
    return '<br>'.join(result)