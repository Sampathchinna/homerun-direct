import pytest
from unittest.mock import patch, MagicMock
from core.mixin_redis import RedisCacheMixin


class DummyUser:
    def __init__(self, user_id, is_superuser=False):
        self.id = user_id
        self.is_superuser = is_superuser


@pytest.fixture
def redis_mixin():
    return RedisCacheMixin()


@patch("core.mixin_redis.cache.get")
def test_get_from_cache(mock_get, redis_mixin):
    mock_get.return_value = {"name": "Test"}
    result = redis_mixin.get_from_cache("TestModel", 1)
    assert result == {"name": "Test"}
    mock_get.assert_called_with("testmodel:1")


@patch("core.mixin_redis.cache.set")
def test_set_to_cache(mock_set, redis_mixin):
    redis_mixin.set_to_cache("TestModel", 1, {"name": "Test"})
    mock_set.assert_called_with("testmodel:1", {"name": "Test"}, timeout=3600)


@patch("core.mixin_redis.cache.delete")
def test_delete_cache(mock_delete, redis_mixin):
    redis_mixin.delete_cache("TestModel", 1)
    mock_delete.assert_called_with("testmodel:1")


def test_get_cache_key(redis_mixin):
    assert redis_mixin.get_cache_key("MyModel", 123) == "mymodel:123"
    assert redis_mixin.get_cache_key("MyModel") == "mymodel"




@patch("django.core.cache.cache.set")
@patch("organization.serializers.OrganizationSerializer")
@patch("organization.models.Organization")
def test_set_user_org_session_superuser(mock_org_model, mock_serializer_class, mock_cache_set, redis_mixin):
    user = DummyUser(user_id=1, is_superuser=True)

    mock_org = MagicMock(id=100)
    mock_org_model.objects.all.return_value = [mock_org]

    mock_serializer_instance = MagicMock()
    mock_serializer_instance.data = {"id": 100, "name": "Org1"}
    mock_serializer_class.return_value = mock_serializer_instance

    redis_mixin.set_user_org_session(user)

    mock_cache_set.assert_any_call("user:1:all_organizations", True, timeout=3600)
    mock_cache_set.assert_any_call("user:1:organization_ids", [100], timeout=3600)
    mock_cache_set.assert_any_call("user:1:organizations", [{"id": 100, "name": "Org1"}], timeout=3600)


@patch("django.core.cache.cache.set")
@patch("organization.serializers.OrganizationSerializer")
@patch("organization.models.Organization")
def test_set_user_org_session_regular_user(mock_org_model, mock_serializer_class, mock_cache_set, redis_mixin):
    user = DummyUser(user_id=2, is_superuser=False)

    mock_org = MagicMock(id=200)
    mock_org_model.objects.filter.return_value = [mock_org]

    mock_serializer_instance = MagicMock()
    mock_serializer_instance.data = {"id": 200, "name": "Org2"}
    mock_serializer_class.return_value = mock_serializer_instance

    redis_mixin.set_user_org_session(user)

    mock_cache_set.assert_any_call("user:2:all_organizations", False, timeout=3600)
    mock_cache_set.assert_any_call("user:2:organization_ids", [200], timeout=3600)
    mock_cache_set.assert_any_call("user:2:organizations", [{"id": 200, "name": "Org2"}], timeout=3600)

@patch("core.mixin_redis.cache.get")
def test_get_user_org_ids(mock_get, redis_mixin):
    user = DummyUser(3)
    mock_get.return_value = [101, 102]
    result = redis_mixin.get_user_org_ids(user)
    assert result == [101, 102]
    mock_get.assert_called_with("user:3:organization_ids", [])


@patch("core.mixin_redis.cache.get")
def test_get_user_orgs(mock_get, redis_mixin):
    user = DummyUser(4)
    mock_get.return_value = [{"id": 1, "name": "TestOrg"}]
    result = redis_mixin.get_user_orgs(user)
    assert result == [{"id": 1, "name": "TestOrg"}]
    mock_get.assert_called_with("user:4:organizations", [])


@patch("core.mixin_redis.cache.get")
def test_has_all_org_access(mock_get, redis_mixin):
    user = DummyUser(5)
    mock_get.return_value = True
    result = redis_mixin.has_all_org_access(user)
    assert result is True
    mock_get.assert_called_with("user:5:all_organizations", False)


@patch("django.core.cache.cache.get")
def test_get_user_org_ids_default_empty(mock_get, redis_mixin):
    user = DummyUser(3)
    mock_get.side_effect = lambda key, default=None: default
    assert redis_mixin.get_user_org_ids(user) == []


@patch("django.core.cache.cache.get")
def test_get_user_orgs_default_empty(mock_get, redis_mixin):
    user = DummyUser(4)
    mock_get.side_effect = lambda key, default=None: default
    assert redis_mixin.get_user_orgs(user) == []


@patch("django.core.cache.cache.get")
def test_has_all_org_access_default_false(mock_get, redis_mixin):
    user = DummyUser(5)
    mock_get.side_effect = lambda key, default=None: default
    assert redis_mixin.has_all_org_access(user) is False





# import pytest
# from unittest.mock import patch, MagicMock
# from core.mixin_redis import RedisCacheMixin


# class DummyUser:
#     def __init__(self, user_id, is_superuser=False):
#         self.id = user_id
#         self.is_superuser = is_superuser


# @pytest.fixture
# def redis_mixin():
#     return RedisCacheMixin()


# @patch("core.mixin_redis.cache.get")
# def test_get_from_cache(mock_get, redis_mixin):
#     mock_get.return_value = {"name": "Test"}
#     result = redis_mixin.get_from_cache("TestModel", 1)
#     assert result == {"name": "Test"}
#     mock_get.assert_called_with("testmodel:1")


# @patch("core.mixin_redis.cache.set")
# def test_set_to_cache(mock_set, redis_mixin):
#     redis_mixin.set_to_cache("TestModel", 1, {"name": "Test"})
#     mock_set.assert_called_with("testmodel:1", {"name": "Test"}, timeout=3600)


# @patch("core.mixin_redis.cache.delete")
# def test_delete_cache(mock_delete, redis_mixin):
#     redis_mixin.delete_cache("TestModel", 1)
#     mock_delete.assert_called_with("testmodel:1")


# def test_get_cache_key(redis_mixin):
#     assert redis_mixin.get_cache_key("MyModel", 123) == "mymodel:123"
#     assert redis_mixin.get_cache_key("MyModel") == "mymodel"


# @patch("core.mixin_redis.cache.set")
# @patch("core.mixin_redis.OrganizationSerializer")
# @patch("core.mixin_redis.Organization.objects.all")
# def test_set_user_org_session_superuser(mock_all, mock_serializer, mock_set, redis_mixin):
#     user = DummyUser(user_id=1, is_superuser=True)
#     mock_org = MagicMock(id=100)
#     mock_all.return_value = [mock_org]
#     mock_serializer.return_value.data = {"id": 100, "name": "Org1"}

#     redis_mixin.set_user_org_session(user)

#     mock_set.assert_any_call("user:1:all_organizations", True, timeout=3600)
#     mock_set.assert_any_call("user:1:organization_ids", [100], timeout=3600)
#     mock_set.assert_any_call("user:1:organizations", [{"id": 100, "name": "Org1"}], timeout=3600)


# @patch("core.mixin_redis.cache.set")
# @patch("core.mixin_redis.OrganizationSerializer")
# @patch("core.mixin_redis.Organization.objects.filter")
# def test_set_user_org_session_regular_user(mock_filter, mock_serializer, mock_set, redis_mixin):
#     user = DummyUser(user_id=2, is_superuser=False)
#     mock_org = MagicMock(id=200)
#     mock_filter.return_value = [mock_org]
#     mock_serializer.return_value.data = {"id": 200, "name": "Org2"}

#     redis_mixin.set_user_org_session(user)

#     mock_set.assert_any_call("user:2:all_organizations", False, timeout=3600)
#     mock_set.assert_any_call("user:2:organization_ids", [200], timeout=3600)
#     mock_set.assert_any_call("user:2:organizations", [{"id": 200, "name": "Org2"}], timeout=3600)


# @patch("core.mixin_redis.cache.get")
# def test_get_user_org_ids(mock_get, redis_mixin):
#     user = DummyUser(3)
#     mock_get.return_value = [101, 102]
#     assert redis_mixin.get_user_org_ids(user) == [101, 102]


# @patch("core.mixin_redis.cache.get")
# def test_get_user_orgs(mock_get, redis_mixin):
#     user = DummyUser(4)
#     mock_get.return_value = [{"id": 1, "name": "TestOrg"}]
#     assert redis_mixin.get_user_orgs(user) == [{"id": 1, "name": "TestOrg"}]


# @patch("core.mixin_redis.cache.get")
# def test_has_all_org_access(mock_get, redis_mixin):
#     user = DummyUser(5)
#     mock_get.return_value = True
#     assert redis_mixin.has_all_org_access(user) is True


# @patch("core.mixin_redis.cache.get")
# def test_get_user_org_ids_default_empty(mock_get, redis_mixin):
#     user = DummyUser(6)
#     mock_get.return_value = None
#     assert redis_mixin.get_user_org_ids(user) == []


# @patch("core.mixin_redis.cache.get")
# def test_get_user_orgs_default_empty(mock_get, redis_mixin):
#     user = DummyUser(7)
#     mock_get.return_value = None
#     assert redis_mixin.get_user_orgs(user) == []


# @patch("core.mixin_redis.cache.get")
# def test_has_all_org_access_default_false(mock_get, redis_mixin):
#     user = DummyUser(8)
#     mock_get.return_value = None
#     assert redis_mixin.has_all_org_access(user) is False
