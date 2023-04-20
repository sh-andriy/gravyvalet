from django.db import models
from django.db.models.query import QuerySet
from django_extensions.db.models import TimeStampedModel


# Create your models here.


class QuerySetExplainMixin:
    def explain(self, *args):
        extra_arguments = ''
        for item in args:
            extra_arguments = (
                '{} {}'.format(extra_arguments, item)
                if isinstance(item, basestring)
                else extra_arguments
            )
        cursor = connections[self.db].cursor()
        query, params = self.query.sql_with_params()
        cursor.execute('explain analyze verbose %s' % query, params)
        return '\n'.join(r[0] for r in cursor.fetchall())


QuerySet = type('QuerySet', (QuerySetExplainMixin, QuerySet), dict(QuerySet.__dict__))


class BaseModel(TimeStampedModel, QuerySetExplainMixin):
    migration_page_size = 50000

    objects = models.QuerySet.as_manager()

    class Meta:
        abstract = True

    def __unicode__(self):
        return '{}'.format(self.id)

    def to_storage(self, include_auto_now=True):
        local_django_fields = set(
            [
                x.name
                for x in self._meta.concrete_fields
                if include_auto_now or not getattr(x, 'auto_now', False)
            ]
        )
        return {name: self.serializable_value(name) for name in local_django_fields}

    @classmethod
    def get_fk_field_names(cls):
        return [
            field.name
            for field in cls._meta.get_fields()
            if field.is_relation
            and not field.auto_created
            and (field.many_to_one or field.one_to_one)
            and not isinstance(field, GenericForeignKey)
        ]

    @classmethod
    def get_m2m_field_names(cls):
        return [
            field.attname or field.name
            for field in cls._meta.get_fields()
            if field.is_relation and field.many_to_many and not hasattr(field, 'field')
        ]

    @classmethod
    def load(cls, data, select_for_update=False):
        try:
            if isinstance(data, basestring):
                # Some models (CitationStyle) have an _id that is not a bson
                # Looking up things by pk will never work with a basestring
                return (
                    cls.objects.get(_id=data)
                    if not select_for_update
                    else cls.objects.filter(_id=data).select_for_update().get()
                )
            return (
                cls.objects.get(pk=data)
                if not select_for_update
                else cls.objects.filter(pk=data).select_for_update().get()
            )
        except cls.DoesNotExist:
            return None

    @property
    def _primary_name(self):
        return '_id'

    @property
    def _is_loaded(self):
        return bool(self.pk)

    def reload(self):
        return self.refresh_from_db()

    def refresh_from_db(self, **kwargs):
        super(BaseModel, self).refresh_from_db(**kwargs)
        # Since Django 2.2, any cached relations are cleared from the reloaded instance.
        #
        # See https://docs.djangoproject.com/en/2.2/ref/models/instances/#django.db.models.Model.refresh_from_db  # noqa: E501
        #
        # However, the default `refresh_from_db()` doesn't refresh related fields. Neither can we
        # refresh related field(s) since it will inevitably cause infinite loop; and
        # Many/One-to-Many relations add to the complexity.
        #
        # The recommended behavior is to explicitly refresh the fields when necessary. In order to
        # preserve pre-upgrade behavior, our customization only reloads GFKs.
        for f in self._meta._get_fields(reverse=False):
            # Note: the following `if` condition is how django internally identifies GFK
            if (
                f.is_relation
                and f.many_to_one
                and not (hasattr(f.remote_field, 'model') and f.remote_field.model)
            ):
                if hasattr(self, f.name):
                    try:
                        getattr(self, f.name).refresh_from_db()
                    except AttributeError:
                        continue

    def clone(self):
        """Create a new, unsaved copy of this object."""
        copy = self.__class__.objects.get(pk=self.pk)
        copy.id = None

        # empty all the fks
        fk_field_names = [
            f.name
            for f in self._meta.model._meta.get_fields()
            if isinstance(f, (ForeignKey, GenericForeignKey))
        ]
        for field_name in fk_field_names:
            setattr(copy, field_name, None)

        try:
            copy._id = bson.ObjectId()
        except AttributeError:
            pass
        return copy

    def save(self, *args, **kwargs):
        # Make Django validate on save (like modm)
        if kwargs.pop('clean', True) and not (
            kwargs.get('force_insert') or kwargs.get('force_update')
        ):
            try:
                self.full_clean()
            except DjangoValidationError as err:
                raise ValidationError(*err.args)
        return super(BaseModel, self).save(*args, **kwargs)
