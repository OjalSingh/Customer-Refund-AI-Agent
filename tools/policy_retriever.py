def retrieve_policy():

    with open(
        "knowledge/refund_policy.txt",
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()