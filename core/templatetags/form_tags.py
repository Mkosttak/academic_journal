# core/templatetags/form_tags.py
from django import template
from django.forms.widgets import CheckboxInput

register = template.Library()

@register.filter(name='add_class')
def add_class(field, css_class):
    existing_classes = field.field.widget.attrs.get('class', '')
    
    if field.errors:
        if existing_classes:
            existing_classes += ' is-invalid'
        else:
            existing_classes = 'is-invalid'

    return field.as_widget(attrs={'class': f'{existing_classes} {css_class}'.strip()})


@register.filter(name='is_checkbox')
def is_checkbox(field):
    return isinstance(field.field.widget, CheckboxInput)