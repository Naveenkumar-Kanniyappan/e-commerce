from django import template
from shop.models import Product

register = template.Library()

@register.filter
def lookup_product(product_id):
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return None

@register.filter
def mul(value, arg):
    return value * arg
