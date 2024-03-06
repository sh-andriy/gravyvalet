from rest_framework import (
    exceptions,
    permissions,
)

from addon_service.models import ResourceReference
from app.authentication import authenticate_resource


class IsAuthenticated(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.session.get("user_reference_uri") is not None


class SessionUserIsOwner(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        session_user_uri = request.session.get("user_reference_uri")
        if session_user_uri:
            return session_user_uri == obj.owner_reference
        return False


class SessionUserCanViewReferencedResource(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return authenticate_resource(request, obj.resource_uri, "read")


class SessionUserIsReferencedResourceAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        resource_uri = None
        try:
           resource_uri = ResourceReference.objects.get(
                id=request.data.get("authoirized_resource", {}).get("id")
            ).resource_uri
        except ResourceReference.DoesNotExist:
            resource_uri = request.data.get("authorized_resource", {}).get("resource_uri")

        if resource_uri is None:
            raise exceptions.ParseError

        return authenticate_resource(request, resource_uri, "admin")
