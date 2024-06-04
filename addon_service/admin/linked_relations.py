from django import forms
from django.contrib.admin import widgets as admin_widgets


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
        self.__related_model = db_relation_field.related_model
        super().__init__(
            required=required,
            label=(label or db_relation_field.name),
            initial=None,
            widget=LinkedRelatedFieldWidgetWrapper(
                widget=LinkedSingleRelationWidget(
                    rel=db_relation_field.remote_field,
                    admin_site=admin_site,
                ),
                rel=db_relation_field.remote_field,
                admin_site=admin_site,
            ),
            help_text=(help_text or db_relation_field.help_text),
        )

    def clean(self, value):
        _pk = super().clean(value)
        return self.__related_model.objects.get(pk=_pk)


class LinkedSingleRelationWidget(admin_widgets.ForeignKeyRawIdWidget):
    choices = ()  # RelatedFieldWidgetWrapper assumes a choices attr :(

    def get_context(self, name, value, attrs):
        _context = super().get_context(name, value, attrs)
        _context["widget"]["attrs"]["readonly"] = True  # readonly input
        return _context


class LinkedRelatedFieldWidgetWrapper(admin_widgets.RelatedFieldWidgetWrapper):
    def get_context(self, name, value, attrs):
        _context = super().get_context(name, value, attrs)
        _context["can_add_related"] = value is None  # may add only if not already
        return _context
