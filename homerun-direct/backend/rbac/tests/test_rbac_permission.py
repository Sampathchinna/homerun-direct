import pytest
from unittest.mock import MagicMock, patch
from rbac.permissions import EntityPermission
from rbac.models import AuthEntityPermission, OrganizatioRole, Organization
from django.contrib.auth import get_user_model

User = get_user_model()
def test_permission_user_not_authenticated():
    request = MagicMock()
    request.user.is_authenticated = False
    view = MagicMock()

    permission = EntityPermission()
    assert permission.has_permission(request, view) is False

def test_permission_no_org_or_group():
    user = MagicMock()
    user.is_authenticated = True
    user.organization = None
    user.group = None

    request = MagicMock()
    request.user = user

    view = MagicMock()
    view.basename = "user"

    permission = EntityPermission()
    assert permission.has_permission(request, view) is False


def test_permission_super_admin():
    group = MagicMock()
    group.is_super_admin = True

    user = MagicMock()
    user.is_authenticated = True
    user.organization = MagicMock()
    user.group = group
    user.username = "superuser"

    request = MagicMock()
    request.user = user
    request.method = "POST"

    view = MagicMock()
    view.basename = "user"

    permission = EntityPermission()
    assert permission.has_permission(request, view) is True


@patch('rbac.permissions.AuthEntityPermission.objects.filter')
def test_permission_not_found(mock_filter):
    mock_filter.return_value.first.return_value = None

    group = MagicMock()
    group.is_super_admin = False

    user = MagicMock()
    user.is_authenticated = True
    user.organization = MagicMock()
    user.group = group
    user.username = "nishant"

    request = MagicMock()
    request.user = user
    request.method = "GET"

    view = MagicMock()
    view.basename = "user"

    permission = EntityPermission()
    assert permission.has_permission(request, view) is False

@patch('rbac.permissions.AuthEntityPermission.objects.filter')
def test_permission_create_denied(mock_filter):
    mock_perm = MagicMock()
    mock_perm.can_create = False
    mock_filter.return_value.first.return_value = mock_perm

    group = MagicMock()
    group.is_super_admin = False

    user = MagicMock()
    user.is_authenticated = True
    user.organization = MagicMock()
    user.group = group

    request = MagicMock()
    request.user = user
    request.method = "POST"

    view = MagicMock()
    view.basename = "user"

    permission = EntityPermission()
    assert permission.has_permission(request, view) is False

@patch('rbac.permissions.AuthEntityPermission.objects.filter')
def test_permission_create_allowed(mock_filter):
    mock_perm = MagicMock()
    mock_perm.can_create = True
    mock_perm.can_read = False
    mock_perm.can_update = False
    mock_perm.can_delete = False
    mock_filter.return_value.first.return_value = mock_perm

    group = MagicMock()
    group.is_super_admin = False

    user = MagicMock()
    user.is_authenticated = True
    user.organization = MagicMock()
    user.group = group

    request = MagicMock()
    request.user = user
    request.method = "POST"

    view = MagicMock()
    view.basename = "user"

    permission = EntityPermission()
    assert permission.has_permission(request, view) is True


@patch('rbac.permissions.AuthEntityPermission.objects.filter')
def test_permission_read_denied(mock_filter):
    mock_perm = MagicMock()
    mock_perm.can_read = False
    mock_filter.return_value.first.return_value = mock_perm

    group = MagicMock()
    group.is_super_admin = False

    user = MagicMock()
    user.is_authenticated = True
    user.organization = MagicMock()
    user.group = group

    request = MagicMock()
    request.user = user
    request.method = "GET"

    view = MagicMock()
    view.basename = "user"

    permission = EntityPermission()
    assert permission.has_permission(request, view) is False


@patch('rbac.permissions.AuthEntityPermission.objects.filter')
def test_permission_update_allowed(mock_filter):
    mock_perm = MagicMock()
    mock_perm.can_update = True
    mock_perm.can_read = False
    mock_perm.can_create = False
    mock_perm.can_delete = False
    mock_filter.return_value.first.return_value = mock_perm

    group = MagicMock()
    group.is_super_admin = False

    user = MagicMock()
    user.is_authenticated = True
    user.organization = MagicMock()
    user.group = group

    request = MagicMock()
    request.user = user
    request.method = "PATCH"

    view = MagicMock()
    view.basename = "user"

    permission = EntityPermission()
    assert permission.has_permission(request, view) is True


@patch('rbac.permissions.AuthEntityPermission.objects.filter')
def test_permission_delete_allowed(mock_filter):
    mock_perm = MagicMock()
    mock_perm.can_delete = True
    mock_perm.can_read = False
    mock_perm.can_create = False
    mock_perm.can_update = False
    mock_filter.return_value.first.return_value = mock_perm

    group = MagicMock()
    group.is_super_admin = False

    user = MagicMock()
    user.is_authenticated = True
    user.organization = MagicMock()
    user.group = group

    request = MagicMock()
    request.user = user
    request.method = "DELETE"

    view = MagicMock()
    view.basename = "user"

    permission = EntityPermission()
    assert permission.has_permission(request, view) is True


































