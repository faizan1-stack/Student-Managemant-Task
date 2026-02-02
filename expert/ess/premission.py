from rest_framework.permissions import BasePermission

class IsVerifiedTeacher(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'teacher' and 
            request.user.is_active
            
        )


class IsVerifiedStudent(BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role == 'student' and
            request.user.is_verified
        )