import redis
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import ConnectionError

client = redis.Redis(host='localhost', port=6379, db=0)
assert client.ping()
es = Elasticsearch("http://localhost:9200")
assert es.ping()
