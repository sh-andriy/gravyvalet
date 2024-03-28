from django.core.exceptions import ValidationError


class InvalidCredentials(ValidationError):
    def __init__(
        self, credentials_issuer, missing_fields, extra_fields, *args, **kwargs
    ):
        self.credentials_issuer = credentials_issuer
        self.missing_fields = missing_fields
        self.extra_fields = extra_fields
        super().__init__(*args, **kwargs)
