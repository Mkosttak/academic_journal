from django import template
from django.utils.safestring import mark_safe
from core.seo_utils import generate_article_schema, generate_organization_schema, generate_breadcrumb

register = template.Library()

@register.simple_tag
def article_schema(article):
    """Makale için Schema.org JSON-LD oluşturur"""
    return mark_safe(generate_article_schema(article))

@register.simple_tag
def organization_schema():
    """Organizasyon için Schema.org JSON-LD oluşturur"""
    return mark_safe(generate_organization_schema())

@register.simple_tag
def breadcrumb_schema(items):
    """Breadcrumb için Schema.org JSON-LD oluşturur"""
    return mark_safe(generate_breadcrumb(items))
