"""decorators for django ModelAdmin for navigable links along read-only relations

largely copied from https://github.com/CenterForOpenScience/SHARE/blob/6f608a7333defd07ad804cce808884e03425e579/share/admin/util.py#L29-L90
"""

from django.urls import reverse
from django.utils.html import format_html


__all__ = (
    "linked_many_field",
    "linked_single_field",
)


def linked_many_field(field_name, order_by=None, select_related=None, defer=None):
    """Decorator for django ModelAdmin; adds links for a *-to-many field"""

    def add_links(cls):
        def links(self, instance):
            linked_qs = getattr(instance, field_name).all()
            if select_related:
                linked_qs = linked_qs.select_related(*select_related)
            if order_by:
                linked_qs = linked_qs.order_by(*order_by)
            if defer:
                linked_qs = linked_qs.defer(*defer)
            return format_html(
                "<ol>{}</ol>",
                format_html(
                    "".join(
                        "<li>{}</li>".format(_admin_link_html(obj)) for obj in linked_qs
                    )
                ),
            )

        links_field = "{}_links".format(field_name)
        links.short_description = field_name.replace("_", " ")  # type: ignore[attr-defined]
        setattr(cls, links_field, links)
        _append_to_cls_property(cls, "readonly_fields", links_field)
        _append_to_cls_property(cls, "exclude", field_name)
        return cls

    return add_links


def linked_single_field(field_name):
    """Decorator for django ModelAdmin that adds a link for a foreign key field"""

    def add_link(cls):
        def link(self, instance):
            linked_obj = getattr(instance, field_name)
            return _admin_link_html(linked_obj)

        link_field = "{}_link".format(field_name)
        link.short_description = field_name.replace("_", " ")  # type: ignore[attr-defined]
        setattr(cls, link_field, link)
        _append_to_cls_property(cls, "readonly_fields", link_field)
        _append_to_cls_property(cls, "exclude", field_name)
        return cls

    return add_link


def _append_to_cls_property(cls, property_name, value):
    old_values = getattr(cls, property_name, None) or []
    setattr(cls, property_name, tuple([*old_values, value]))


def _admin_url(linked_obj):
    return reverse(
        "admin:{}_{}_change".format(
            linked_obj._meta.app_label,
            linked_obj._meta.model_name,
        ),
        args=[linked_obj.id],
    )


def _admin_link_html(linked_obj):
    url = _admin_url(linked_obj)
    return format_html('<a href="{}">{}</a>', url, repr(linked_obj))
