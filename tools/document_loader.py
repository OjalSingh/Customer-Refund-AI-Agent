import os


def load_document_contents(doc_names):

    documents = {}

    for doc in doc_names:

        path = os.path.join("policies", doc)

        try:
            with open(path, "r", encoding="utf-8") as f:
                documents[doc] = f.read()

        except Exception as e:
            documents[doc] = f"Error loading document: {e}"

    return documents