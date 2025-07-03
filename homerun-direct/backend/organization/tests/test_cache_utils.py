# test_cache_utils.py

import json
import pytest
from unittest.mock import patch, MagicMock
from django.utils.timezone import now
from organization.cache_utils import update_cache


@pytest.fixture
def mock_organization():
    mock_user = MagicMock()
    mock_user.email = "user@example.com"
    
    mock_subscription_plan = MagicMock()
    mock_subscription_plan.name = "Pro"
    
    mock_location = MagicMock()
    mock_location.street_address = "123 Main St"
    mock_location.city = "Metropolis"
    mock_location.state_province = "State"
    mock_location.postal_code = "12345"
    mock_location.country = "Country"
    mock_location.latitude = "40.7128"
    mock_location.longitude = "-74.0060"

    mock_org = MagicMock()
    mock_org.id = 1
    mock_org.organization_name = "TestOrg"
    mock_org.user = mock_user
    mock_org.subscription_plan = mock_subscription_plan
    mock_org.stripe_subscription_id = "sub_12345"
    mock_org.is_organization_created = True
    mock_org.is_payment_done = True
    mock_org.location = mock_location
    mock_org.created_at = now()

    return mock_org


@patch("organization.cache_utils.redis_client.set")
@patch("organization.cache_utils.es_client.index")
def test_update_cache_full_data(mock_es_index, mock_redis_set, mock_organization):
    update_cache(mock_organization)

    expected_key = f"organization:{mock_organization.id}"
    redis_call_args = mock_redis_set.call_args[0]
    es_call_args = mock_es_index.call_args[1]

    assert redis_call_args[0] == expected_key
    assert isinstance(json.loads(redis_call_args[1]), dict)
    assert es_call_args["index"] == "organizations"
    assert es_call_args["id"] == mock_organization.id
    assert isinstance(es_call_args["body"], dict)


@patch("organization.cache_utils.redis_client.set")
@patch("organization.cache_utils.es_client.index")
def test_update_cache_with_missing_optional_fields(mock_es_index, mock_redis_set):
    mock_org = MagicMock()
    mock_org.id = 2
    mock_org.organization_name = "PartialOrg"
    mock_org.user = None
    mock_org.subscription_plan = None
    mock_org.stripe_subscription_id = None
    mock_org.is_organization_created = False
    mock_org.is_payment_done = False
    mock_org.location = None
    mock_org.created_at = now()

    update_cache(mock_org)

    redis_data = json.loads(mock_redis_set.call_args[0][1])
    assert redis_data["user_email"] is None
    assert redis_data["subscription_plan"] is None
    assert redis_data["location"]["city"] is None


def test_update_cache_with_none_input():
    # Should simply return without doing anything
    assert update_cache(None) is None


@patch("organization.cache_utils.redis_client.set", side_effect=ConnectionError("Redis down"))
@patch("organization.cache_utils.es_client.index")
def test_redis_down(mock_es_index, mock_redis_set, mock_organization):
    with pytest.raises(ConnectionError):
        update_cache(mock_organization)


@patch("organization.cache_utils.redis_client.set")
@patch("organization.cache_utils.es_client.index", side_effect=ConnectionError("Elasticsearch down"))
def test_elasticsearch_down(mock_es_index, mock_redis_set, mock_organization):
    with pytest.raises(ConnectionError):
        update_cache(mock_organization)


@patch("organization.cache_utils.redis_client.set")
@patch("organization.cache_utils.es_client.index")
def test_invalid_latitude(mock_es_index, mock_redis_set):
    mock_org = MagicMock()
    mock_org.id = 3
    mock_org.organization_name = "BadLocationOrg"
    mock_org.user = MagicMock(email="user@example.com")
    mock_org.subscription_plan = MagicMock(name="Basic")
    mock_org.stripe_subscription_id = "sub_99999"
    mock_org.is_organization_created = True
    mock_org.is_payment_done = True
    mock_org.location = MagicMock(
        street_address="456 Elm St",
        city="Gotham",
        state_province="Province",
        postal_code="54321",
        country="Land",
        latitude="invalid",  # Should raise ValueError
        longitude="30.0"
    )
    mock_org.created_at = now()

    with pytest.raises(ValueError):
        update_cache(mock_org)


@patch("organization.cache_utils.redis_client.set")
@patch("organization.cache_utils.es_client.index")
def test_missing_created_at(mock_es_index, mock_redis_set):
    mock_org = MagicMock()
    mock_org.id = 4
    mock_org.organization_name = "NoDateOrg"
    mock_org.user = MagicMock(email="user@example.com")
    mock_org.subscription_plan = MagicMock(name="Premium")
    mock_org.stripe_subscription_id = "sub_77777"
    mock_org.is_organization_created = True
    mock_org.is_payment_done = True
    mock_org.location = None
    mock_org.created_at = None  # Should raise AttributeError on isoformat

    with pytest.raises(AttributeError):
        update_cache(mock_org)










# # test_cache_utils.py

# import json
# import pytest
# from unittest.mock import patch, MagicMock
# from django.utils.timezone import now
# from organization.cache_utils import update_cache


# @pytest.fixture
# def mock_organization():
#     mock_user = MagicMock(email="user@example.com")
#     mock_subscription_plan = MagicMock(name="Pro")
#     mock_location = MagicMock(
#         street_address="123 Main St",
#         city="Metropolis",
#         state_province="State",
#         postal_code="12345",
#         country="Country",
#         latitude="40.7128",
#         longitude="-74.0060"
#     )

#     mock_org = MagicMock(
#         id=1,
#         organization_name="TestOrg",
#         user=mock_user,
#         subscription_plan=mock_subscription_plan,
#         stripe_subscription_id="sub_12345",
#         is_organization_created=True,
#         is_payment_done=True,
#         location=mock_location,
#         created_at=now()
#     )

#     return mock_org


# @patch("organization.cache_utils.redis_client.set")
# @patch("organization.cache_utils.es_client.index")
# def test_update_cache_full_data(mock_es_index, mock_redis_set, mock_organization):
#     update_cache(mock_organization)

#     expected_key = f"organization:{mock_organization.id}"
#     redis_call_args = mock_redis_set.call_args[0]
#     es_call_args = mock_es_index.call_args[1]

#     assert redis_call_args[0] == expected_key
#     assert isinstance(json.loads(redis_call_args[1]), dict)
#     assert es_call_args["index"] == "organizations"
#     assert es_call_args["id"] == mock_organization.id
#     assert isinstance(es_call_args["body"], dict)


# @patch("organization.cache_utils.redis_client.set")
# @patch("organization.cache_utils.es_client.index")
# def test_update_cache_with_missing_optional_fields(mock_es_index, mock_redis_set):
#     mock_org = MagicMock(
#         id=2,
#         organization_name="PartialOrg",
#         user=None,
#         subscription_plan=None,
#         stripe_subscription_id=None,
#         is_organization_created=False,
#         is_payment_done=False,
#         location=None,
#         created_at=now()
#     )

#     update_cache(mock_org)

#     redis_data = json.loads(mock_redis_set.call_args[0][1])
#     assert redis_data["user_email"] is None
#     assert redis_data["subscription_plan"] is None
#     assert redis_data["location"]["city"] is None


# def test_update_cache_with_none_input():
#     # Should simply return without doing anything
#     assert update_cache(None) is None


# @patch("organization.cache_utils.redis_client.set", side_effect=ConnectionError("Redis down"))
# @patch("organization.cache_utils.es_client.index")
# def test_redis_down(mock_es_index, mock_redis_set, mock_organization):
#     with pytest.raises(ConnectionError):
#         update_cache(mock_organization)


# @patch("organization.cache_utils.redis_client.set")
# @patch("organization.cache_utils.es_client.index", side_effect=ConnectionError("Elasticsearch down"))
# def test_elasticsearch_down(mock_es_index, mock_redis_set, mock_organization):
#     with pytest.raises(ConnectionError):
#         update_cache(mock_organization)


# @patch("organization.cache_utils.redis_client.set")
# @patch("organization.cache_utils.es_client.index")
# def test_invalid_latitude(mock_es_index, mock_redis_set):
#     mock_org = MagicMock(
#         id=3,
#         organization_name="BadLocationOrg",
#         user=MagicMock(email="user@example.com"),
#         subscription_plan=MagicMock(name="Basic"),
#         stripe_subscription_id="sub_99999",
#         is_organization_created=True,
#         is_payment_done=True,
#         location=MagicMock(
#             street_address="456 Elm St",
#             city="Gotham",
#             state_province="Province",
#             postal_code="54321",
#             country="Land",
#             latitude="invalid",  # Should raise ValueError
#             longitude="30.0"
#         ),
#         created_at=now()
#     )

#     with pytest.raises(ValueError):
#         update_cache(mock_org)


# @patch("organization.cache_utils.redis_client.set")
# @patch("organization.cache_utils.es_client.index")
# def test_missing_created_at(mock_es_index, mock_redis_set):
#     mock_org = MagicMock(
#         id=4,
#         organization_name="NoDateOrg",
#         user=MagicMock(email="user@example.com"),
#         subscription_plan=MagicMock(name="Premium"),
#         stripe_subscription_id="sub_77777",
#         is_organization_created=True,
#         is_payment_done=True,
#         location=None,
#         created_at=None  # Should raise AttributeError on isoformat
#     )

#     with pytest.raises(AttributeError):
#         update_cache(mock_org)
