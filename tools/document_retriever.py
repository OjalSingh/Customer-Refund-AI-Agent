import os

def retrieve_relevant_docs(workflow):
    """
    Maps the active workflow to its corresponding text policy file.
    """
    filename = f"{workflow}_policy.txt"
    path = os.path.join("policies", filename)
    
    if os.path.exists(path):
        return [filename]
    return []