from elasticsearch import Elasticsearch


client = Elasticsearch(HOST="http://localhost", PORT=9200)
index = 'tamilactors'


def search(query):
    # Process basic query search
    body = basic_search(query)
    response = client.search(index=index, body=body)
    return response


def basic_search(query):
    q = {
        "query": {
            "query_string": {
                "query": query
            }
        }
    }
    return q


def single_match_search(query, field):
    q = {
        "query": {
            "match": {
                field: query
            }
        }
    }
    return q


def multi_match_search(query, fields, operator='or'):
    q = {
        "query": {
            "multi_match": {
                "query": query,
                "fields": fields,
                "operator": operator,
                "type": "best_fields"
            }
        }
    }
    return q
