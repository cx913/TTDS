from ..models import TokenData

def create_tokens_from_dict(my_dict):
    for token, doc_ids in my_dict.items():
        for doc_id, data in doc_ids.items():
            token_data = TokenData(token=token, doc_id=doc_id, data=data)
            token_data.save()