from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()


# Filter permissions 
@register.filter
def filter_permissions(queryset):
    """Exclude unwanted permissions based on content type and name."""
    excluded_models = {"logentry", "session", "contenttype"}
    excluded_permissions = {"add_permission", "delete_permission"}

    return [
        perm for perm in queryset 
        if perm.content_type.model not in excluded_models and 
           not (perm.content_type.model == "permission" and perm.codename in excluded_permissions)
    ]