import bson
import jwe
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.postgres.fields import ArrayField  # replace with sqlite equiv?
from django.core.exceptions import ValidationError
from django.db import connections, models
from django.db.models import DateTimeField, ForeignKey, TextField
from django.db.models.query import QuerySet
from django_extensions.db.models import TimeStampedModel

import charon.settings as charon_settings

SENSITIVE_DATA_KEY = jwe.kdf(
    charon_settings.SENSITIVE_DATA_SECRET.encode('utf-8'),
    charon_settings.SENSITIVE_DATA_SALT.encode('utf-8'),
)


# Create your models here.


def generate_object_id():
    return str(bson.ObjectId())


def ensure_bytes(value):
    """Helper function to ensure all inputs are encoded to the proper value utf-8 value
    regardless of input type"""
    if isinstance(value, bytes):
        return value
    return value.encode('utf-8')


def ensure_str(value):
    if isinstance(value, bytes):
        return value.decode()
    return value


def encrypt_string(value, prefix='jwe:::'):
    prefix = ensure_bytes(prefix)
    if value:
        value = ensure_bytes(value)
        if value and not value.startswith(prefix):
            value = (prefix + jwe.encrypt(value, SENSITIVE_DATA_KEY)).decode()
    return value


def decrypt_string(value, prefix='jwe:::'):
    prefix = ensure_bytes(prefix)
    if value:
        value = ensure_bytes(value)
        if value.startswith(prefix):
            value = jwe.decrypt(value[len(prefix) :], SENSITIVE_DATA_KEY).decode()
    return value


class NaiveDatetimeException(Exception):
    pass


class EncryptedTextField(TextField):
    """
    This field transparently encrypts data in the database. It should probably only be
    used with PG unless the user takes into account the db specific trade-offs with
    TextFields.
    """

    prefix = 'jwe:::'

    def get_db_prep_value(self, value, **kwargs):
        return encrypt_string(value, prefix=self.prefix)

    def to_python(self, value):
        return decrypt_string(value, prefix=self.prefix)

    def from_db_value(self, value, expression, connection):
        return self.to_python(value)


class NonNaiveDateTimeField(DateTimeField):
    def get_prep_value(self, value):
        value = super(NonNaiveDateTimeField, self).get_prep_value(value)
        if value is not None and (
            value.tzinfo is None or value.tzinfo.utcoffset(value) is None
        ):
            raise NaiveDatetimeException('Tried to encode a naive datetime.')
        return value


class QuerySetExplainMixin:
    def explain(self, *args):
        extra_arguments = ''
        for item in args:
            extra_arguments = (
                '{} {}'.format(extra_arguments, item)
                if isinstance(item, str)
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
        # However, the default `refresh_from_db()` doesn't refresh related fields.
        # Neither can we refresh related field(s) since it will inevitably cause
        # infinite loop; and Many/One-to-Many relations add to the complexity.
        #
        # The recommended behavior is to explicitly refresh the fields when necessary.
        # In order to preserve pre-upgrade behavior, our customization only reloads GFKs
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
            except ValidationError as err:
                raise ValidationError(*err.args)
        return super(BaseModel, self).save(*args, **kwargs)


class BaseIDMixin(models.Model):
    class Meta:
        abstract = True


class ObjectIDMixin(BaseIDMixin):
    primary_identifier_name = '_id'

    _id = models.CharField(
        max_length=24, default=generate_object_id, unique=True, db_index=True
    )

    def __unicode__(self):
        return '_id: {}'.format(self._id)

    @classmethod
    def load(cls, q, select_for_update=False):
        try:
            return (
                cls.objects.get(_id=q)
                if not select_for_update
                else cls.objects.filter(_id=q).select_for_update().get()
            )
        except cls.DoesNotExist:
            # modm doesn't throw exceptions when loading things that don't exist
            return None

    class Meta:
        abstract = True


class ExternalAccount(ObjectIDMixin, BaseModel):
    """An account on an external service.

    Note that this object is not and should not be aware of what other objects
    are associated with it. This is by design, and this object should be kept as
    thin as possible, containing only those fields that must be stored in the
    database.

    The ``provider`` field is a de facto foreign key to an ``ExternalProvider``
    object, as providers are not stored in the database.
    """

    # The OAuth credentials. One or both of these fields should be populated.
    # For OAuth1, this is usually the "oauth_token"
    # For OAuth2, this is usually the "access_token"
    oauth_key = EncryptedTextField(blank=True, null=True)

    # For OAuth1, this is usually the "oauth_token_secret"
    # For OAuth2, this is not used
    oauth_secret = EncryptedTextField(blank=True, null=True)

    # Used for OAuth2 only
    refresh_token = EncryptedTextField(blank=True, null=True)
    date_last_refreshed = NonNaiveDateTimeField(blank=True, null=True)
    expires_at = NonNaiveDateTimeField(blank=True, null=True)
    scopes = ArrayField(models.CharField(max_length=128), default=list, blank=True)

    # The `name` of the service
    # This lets us query for only accounts on a particular provider
    # TODO We should make provider an actual FK someday.
    provider = models.CharField(max_length=50, blank=False, null=False)
    # The proper 'name' of the service
    # Needed for account serialization
    provider_name = models.CharField(max_length=255, blank=False, null=False)

    # The unique, persistent ID on the remote service.
    provider_id = models.CharField(max_length=255, blank=False, null=False)

    # The user's name on the external service
    display_name = EncryptedTextField(blank=True, null=True)
    # A link to the user's profile on the external service
    profile_url = EncryptedTextField(blank=True, null=True)

    def __repr__(self):
        return '<ExternalAccount: {}/{}>'.format(self.provider, self.provider_id)

    def _natural_key(self):
        if self.pk:
            return self.pk
        return hash(str(self.provider_id) + str(self.provider))

    class Meta:
        unique_together = [
            (
                'provider',
                'provider_id',
            )
        ]
