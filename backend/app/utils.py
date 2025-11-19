import json


def authors_to_json(authors):
    if isinstance(authors, str):
        return authors
    return json.dumps(authors)