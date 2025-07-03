import pytest
from unittest.mock import Mock
from django.core.exceptions import PermissionDenied
from rbac.org_level_permission import apply_organization_level_filter, apply_brand_level_filter

def test_apply_organization_level_filter_superuser():
    request = Mock()
    request.user.is_superuser = True
    must_clauses = []
    
    apply_organization_level_filter(request, must_clauses)
    
    assert must_clauses == []

def test_apply_organization_level_filter_with_org_ids():
    request = Mock()
    request.user.is_superuser = False
    request.session.get = Mock(return_value=[1, 2, 3])
    must_clauses = []

    apply_organization_level_filter(request, must_clauses)

    assert must_clauses == [{
        "terms": {
            "id": [1, 2, 3]
        }
    }]

def test_apply_organization_level_filter_without_org_ids(capfd):
    request = Mock()
    request.user.is_superuser = False
    request.session.get = Mock(return_value=[])
    must_clauses = []

    apply_organization_level_filter(request, must_clauses)

    out, _ = capfd.readouterr()
    assert "No organization_ids found in session" in out
    assert must_clauses == []


def test_apply_brand_level_filter_superuser():
    request = Mock()
    request.user.is_superuser = True
    must_clauses = []

    apply_brand_level_filter(request, must_clauses)

    assert must_clauses == []

def test_apply_brand_level_filter_with_brand_ids(capfd):
    request = Mock()
    request.user.is_superuser = False
    request.session.get = Mock(return_value=[101, 202])
    must_clauses = []

    apply_brand_level_filter(request, must_clauses)

    out, _ = capfd.readouterr()
    assert "Noooooooooooooooooooooooooot Suuuuuuuuuuuuuuuuuuuuuuuper" in out
    assert must_clauses == [{
        "terms": {
            "id": [101, 202]
        }
    }]

def test_apply_brand_level_filter_without_brand_ids():
    request = Mock()
    request.user.is_superuser = False
    request.session.get = Mock(return_value=[])

    with pytest.raises(PermissionDenied, match="No brand access defined for this user."):
        apply_brand_level_filter(request, [])

