from rest_framework import permissions
# from allauth.account.admin import EmailAddress
import logging

class IsAdminOrOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(*args):
        return (IsAdminOrReadOnly.has_permission(*args) or IsOwner.has_permission(*args))