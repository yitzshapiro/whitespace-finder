import logging

def handle_errors(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error occurred: {str(e)}")
            return None
    return wrapper

def validate_search_terms(terms):
    if not terms or not isinstance(terms, list) or not all(isinstance(term, str) for term in terms):
        raise ValueError("Search terms must be a list of non-empty strings.")
    return terms
