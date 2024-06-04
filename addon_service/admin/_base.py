import enum
import typing

from django import forms
from django.contrib import admin

from addon_service.admin.linked_relations import LinkedSingleRelationFormField


__all__ = ("GravyvaletModelAdmin",)


class GravyvaletModelAdmin(admin.ModelAdmin):
    linked_fk_fields: typing.Iterable[str] = ()
    enum_choice_fields: dict[str, type[enum.Enum]] | None = None

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in self.linked_fk_fields:
            return LinkedSingleRelationFormField(
                required=False,
                db_relation_field=db_field,
                admin_site=self.admin_site,
            )
        if self.enum_choice_fields and db_field.name in self.enum_choice_fields:
            _enum = self.enum_choice_fields[db_field.name]
            return forms.ChoiceField(
                label=db_field.verbose_name,
                choices=[
                    (None, ""),
                    *((_member.value, _member.name) for _member in _enum),
                ],
            )
        return super().formfield_for_dbfield(db_field, request, **kwargs)
