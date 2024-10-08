from elasticsearch import Elasticsearch
from .constants import esconsts

#* Create an Elasticsearch client
es = Elasticsearch([esconsts.ES_ENDPOINT])

#* Function to create an index if it does not exist.
def create_index(index_name):
    if not es.indices.exists(index = index_name):
        es.indices.create(
            index=index_name,
            body={
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                },
                "mappings": {
                    "properties": {
                        "userid": {"type": "integer"},
                        "username": {"type": "text"},
                        "nickname": {"type": "text"},
                        "major": {"type": "text"},
                        "email": {"type": "keyword"},
                        "role": {"type": "keyword"},
                    }
                }
            }
        )

#* Function to index user details in Elasticsearch.
def index_user(index_name, user_id, user_document):
    es.index(index=index_name, id=user_id, body=user_document)