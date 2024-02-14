
class SessionUserIsAccountOwner(): #Add appropriate base class

    def get_user_uri_for_view(self, view):
        raise NotImplementedError('Subclass must implement this')

    def has_object_permission(self, request, view, obj):
        session_user_uri = request.session.get('user_reference_uri')
        return session_user_uri == obj.account_owner.uri


class IsAuthenticated:

    def has_permission(self, request, view):
        return request.session.get('user_reference_uri') is not None
