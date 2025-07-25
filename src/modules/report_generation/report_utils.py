import numpy as np

def similarity_score(i:str, t:str, q:str, alpha:float):
    """Returns the similarity score between a piece of information i, a topic t, and a question q.
    i,t,q are compared as text embeddings
    """
    raise NotImplementedError
    return np.cos(i,t)**alpha * (1-np.cos(i,q))**(1-alpha)

def retrieve(search_queries: list[str]) -> list[str]: # I dont know what shape this data takes yet 
    raise NotImplementedError
    def retrieval_api(search_queries: list[str]) -> list[str]:
        pass
    def rerank(documents: list[str]) -> list[str]:
        pass
    def filter_documents(documents: list[str]) -> list[str]:
        pass
    documents = retrieval_api(search_queries)
    documents = rerank(documents)
    documents = filter_documents(documents)
    return documents


