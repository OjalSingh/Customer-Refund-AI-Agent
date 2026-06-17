def retrieve_policy():

    with open(
        "policies/refund_policy.txt",
        "r",
        encoding="utf-8"
    ) as file:

        return file.read()