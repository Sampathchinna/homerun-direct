import pytest
from unittest.mock import MagicMock, patch
from core.mixin_es import ElasticsearchIndexMixin, ElasticSearchMixin
from unittest.mock import MagicMock

from organization.models import Location  # Import the actual model
# Mock instance for model
class MockModel:
    pk = 1

    class _meta:
        fields = []

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@pytest.fixture
def mixin():
    return ElasticSearchMixin()


@patch("core.mixin_es.es.index")
def test_index_instance_success(mock_index, mixin):
    instance = MockModel(name="Test", pk=1)
    mixin.index_instance(instance, "test-index")
    mock_index.assert_called_once()


@patch("core.mixin_es.es.delete")
def test_clear_index_success(mock_delete, mixin):
    instance = MockModel(pk=1)
    mixin.clear_index(instance, "test-index")
    mock_delete.assert_called_once_with(index="test-index", id=1, ignore=[404])


@patch("core.mixin_es.bulk")
def test_bulk_index_queryset_success(mock_bulk, mixin):
    queryset = [MockModel(pk=i, name=f"obj{i}") for i in range(3)]
    for obj in queryset:
        obj._meta.fields = []

    mixin.bulk_index_queryset(queryset, "test-index")
    assert mock_bulk.called
    assert mock_bulk.call_args[0][1][0]["_index"] == "test-index"




def test_serialize_instance_with_location():
    mixin = ElasticsearchIndexMixin()
    instance = MagicMock()
    instance._meta.fields = []

    # Simulate a proper Location instance
    location = Location(
        street_address="123 Main St",
        apt_suite="Apt 4B",
        city="Metropolis",
        state_province="NY",
        postal_code="10001",
        country="USA",
        latitude=40.7128,
        longitude=-74.0060
    )

    # Attach mocked Location
    instance.location = location

    result = mixin.serialize_instance(instance)

    assert result["street_address"] == "123 Main St"
    assert result["apt_suite"] == "Apt 4B"
    assert result["city"] == "Metropolis"
    assert result["state_province"] == "NY"
    assert result["postal_code"] == "10001"
    assert result["country"] == "USA"
    assert result["latitude"] == 40.7128
    assert result["longitude"] == -74.0060



@patch("core.mixin_es.es.search")
def test_search_elasticsearch_success(mock_search, mixin):
    mock_search.return_value = {
        "hits": {
            "hits": [
                {"_source": {"name": "Test1"}},
                {"_source": {"name": "Test2"}}
            ]
        }
    }
    result = mixin.search_elasticsearch("test-index", {"match_all": {}}, page=1, per_page=2)
    assert len(result) == 2
    assert result[0]["name"] == "Test1"


def test_build_elasticsearch_filters_basic():
    mixin = ElasticSearchMixin()
    params = {
        "status": "active",
        "age__gte": "18",
        "category__in": "a,b,c",
        "verified": "true",
        "nested.field__icontains": "hello"
    }
    filters = mixin.build_elasticsearch_filters(params)

    assert {"match": {"status": "active"}} in filters
    assert any("range" in f.get("range", {}) or "range" in str(f) for f in filters)
    assert any("terms" in f.get("terms", {}) or "terms" in str(f) for f in filters)
    assert any("term" in f.get("term", {}) or "term" in str(f) for f in filters)
    assert any("nested" in f for f in filters)


def test_build_elasticsearch_filters_invalid_key():
    mixin = ElasticSearchMixin()
    params = {"some*weird&key": "val"}
    filters = mixin.build_elasticsearch_filters(params)
    assert filters[0] == {"match": {"some*weird&key": "val"}}


@patch("core.mixin_es.es.index", side_effect=Exception("ES down"))
def test_index_instance_failure(mock_index, mixin):
    instance = MockModel(name="Fail")
    with pytest.raises(Exception) as excinfo:
        mixin.index_instance(instance, "fail-index")
    assert "ES down" in str(excinfo.value)
