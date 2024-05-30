from django import forms
from django.contrib.admin import widgets as admin_widgets
from django.urls import reverse
from django.utils.html import format_html


class LinkedSingleRelationFormField(forms.Field):
    def __init__(
        self,
        *,
        required,
        db_relation_field,
        admin_site,
        label=None,
        help_text=None,
    ):
        super().__init__(
            required=required,
            label=(label or db_relation_field.name),
            initial=None,
            widget=LinkedSingleRelationWidget(
                rel=db_relation_field.remote_field,
                admin_site=admin_site,
            ),
            help_text=(help_text or db_relation_field.help_text),
        )

    def clean(self): ...


class LinkedSingleRelationWidget(admin_widgets.ForeignKeyRawIdWidget):
    choices = ()

    def render(self, name, value, attrs=None, renderer=None):
        _context = self.get_context(name, value, attrs)
        _url = _context.get("link_url")
        if _url:
            _label = _context.get("link_label")
            return format_html('<a href="{}">{}</a>', _url, _label)
        return format_html(str(None))


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
