from django.core.exceptions import ValidationError

class InvalidCredentialsError(ValidationError):

    def __init__(self, credentials_format, missing_fields, extra_fields, *args, **kwargs):
        self.credentials_format = credentials_format
        self.missing_fields = missing_fields
        self.extra_fields = extra_fields
        super().__init__(*args, **kwargs)
