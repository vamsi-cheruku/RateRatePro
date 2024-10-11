from opensearchpy import OpenSearch

client = OpenSearch(
    hosts=[{'host': 'https://search-rateratepro-v6v5ugewbfvijd7akccrma7pry.aos.us-east-1.on.aws', 'port': 443}],
    http_auth=('admin', 'OpenSearch@007'),
    # use_ssl=True,
    # verify_certs=True
)

#* Function to create an index if it does not exist.
def create_user_index(index_name):
    if not client.indices.exists(index = index_name):
        client.indices.create(
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
    client.index(index=index_name, id=user_id, body=user_document)
