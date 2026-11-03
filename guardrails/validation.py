APPROVE = "APPROVE"


def validate_decision(user, transactions, result):
    """Last safety barrier: an APPROVE must always rest on a verified user, a ledger entry and a cited clause."""
    if result.decision != APPROVE:
        return True, "Decision validated"
    if user is None:
        return False, "User verification failed"
    if not transactions or not result.target_txn_ids:
        return False, "No transactions support an approval"
    if not result.clause:
        return False, "Approval has no policy clause"
    return True, "Decision validated"
