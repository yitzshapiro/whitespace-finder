import ollama
import json


def generate_search_terms(prompt, model="llama3.1:latest"):
    response = ollama.generate(
        model=model, prompt=prompt, format="json", options={"temperature": 0.1}
    )
    if response and "response" in response:
        search_terms_json = json.loads(response["response"])
        print(search_terms_json)
        search_terms = search_terms_json.get("search_terms", [])
        if not search_terms:
            raise ValueError("No search terms found in the response.")
        return search_terms
    raise ValueError("Failed to generate search terms from Ollama.")
