import dataclasses

from rest_framework import mixins as drf_mixins
from rest_framework.exceptions import (
    NotFound,
    PermissionDenied,
)
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import (
    GenericViewSet,
    ViewSet,
)
from rest_framework_json_api.views import (
    AutoPrefetchMixin,
    PreloadIncludesMixin,
    ReadOnlyModelViewSet,
    RelatedMixin,
)

from .jsonapi import extract_filter_expressions


class _DrfJsonApiHelpers(AutoPrefetchMixin, PreloadIncludesMixin, RelatedMixin):
    pass


class RestrictedReadOnlyViewSet(ReadOnlyModelViewSet):
    def list(self, request, *args, **kwargs):
        filters = extract_filter_expressions(self.request.GET)
        if self.required_list_filter not in filters:
            raise ValidationError(
                f"Request is missing required filter {self.required_list_filter}"
            )
        qs = self.get_queryset().filter(**filters)
        try:
            self.check_object_permissions(self.request, qs.get())
        except qs.model.DoesNotExist:
            raise NotFound("Provided filter returned no results.")
        except qs.model.MultipleObjectsReturned:
            print("multiple objects returned?")
            raise PermissionDenied(
                "Filters to this endpoint must be uniquely identifying"
            )

        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)


class RetrieveWriteViewSet(
    _DrfJsonApiHelpers,
    drf_mixins.CreateModelMixin,
    drf_mixins.RetrieveModelMixin,
    drf_mixins.UpdateModelMixin,
    drf_mixins.DestroyModelMixin,
    GenericViewSet,
):
    http_method_names = ["get", "post", "patch", "delete", "head", "options"]


class DataclassViewset(ViewSet, RelatedMixin):
    http_method_names = ["get", "head", "options"]

    # set in subclasses:
    serializer_class: type  # should have a dataclass at serializer_class.Meta.model

    def retrieve(self, request, pk):
        _obj = self.dataclass_model.get_by_pk(pk)
        _serializer = self.get_serializer_class()(
            _obj, context=self.get_serializer_context()
        )
        return Response(_serializer.data)

    # for RelatedMixin
    def get_object(self):
        return self.dataclass_model.get_by_pk(self.kwargs["pk"])

    # for RelatedMixin
    def get_serializer_class(self):
        return self.serializer_class

    # for RelatedMixin
    def get_serializer_context(self):
        return {"request": self.request}

    @property
    def dataclass_model(self):
        _model = self.serializer_class.Meta.model  # type: ignore
        assert dataclasses.is_dataclass(_model) and isinstance(_model, type)
        return _model
