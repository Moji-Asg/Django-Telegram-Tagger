from django import template
from django.conf import settings


register = template.Library()


@register.simple_tag
def get_area_describedby(obj):
    return obj.field.widget.attrs['area-describedby']


@register.simple_tag
def get_groups(obj):
    unique_groups = []
    for field in obj.fields.values():
        if field.group in unique_groups:
            continue

        unique_groups.append(field.group)

    result = []
    for group in unique_groups:
        group_name = settings.DEFAULT_SETTINGS[group]

        attrs = {
            'name': group_name,
            'code': group
        }

        result.append(
            type('Group', (), attrs)
        )

    return result

@register.simple_tag
def get_fields_by_group(obj, group):
    result = []
    for key, field in obj.fields.items():
        if field.group == group.code:
            result.append(obj[key])

    return result
