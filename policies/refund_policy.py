def evaluate_refund(investigation):

    if investigation["duplicate"]:
        return {
            "eligible": True,
            "reasoning": investigation["reasons"]
        }

    return {
        "eligible": False,
        "reasoning": investigation["reasons"]
    }