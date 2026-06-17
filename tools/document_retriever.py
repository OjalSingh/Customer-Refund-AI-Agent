import os


def retrieve_relevant_docs(intent):

    matches = []

    for filename in os.listdir("policies"):

        if not filename.endswith(".txt"):
            continue

        if "refund" in intent.lower():

            if "refund" in filename.lower():
                matches.append(filename)

    return matches