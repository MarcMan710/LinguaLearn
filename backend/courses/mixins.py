from rest_framework.permissions import IsAuthenticated

class UserQuerysetMixin:
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user) 