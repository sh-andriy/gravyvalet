import typing

from django.contrib import admin

from addon_service.admin.widgets import LinkedSingleRelationFormField


__all__ = ("ModelAdminWithLinks",)


class ModelAdminWithLinks(admin.ModelAdmin):
    linked_fk_fields: typing.Iterable[str] = ()
    # linked_many_fields: tuple[str, ...] = ()

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        if db_field.name in self.linked_fk_fields:
            return LinkedSingleRelationFormField(
                required=False,
                db_relation_field=db_field,
                admin_site=self.admin_site,
            )
        return super().formfield_for_dbfield(db_field, request, **kwargs)
