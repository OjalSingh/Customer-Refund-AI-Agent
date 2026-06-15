class AgentState:

    def __init__(self, user_message):

        self.state = {
            "user_message": user_message,
            "intent": None,
            "merchant": None,

            "user_id": None,
            "user": None,

            "transactions": [],
            "policy": None,

            "policy_result": None,
            "risk_result": None,

            "decision": None,

            "audit_log": []
        }

    def update(self, key, value):
        self.state[key] = value

    def log(self, message):
        self.state["audit_log"].append(message)

    def get(self):
        return self.state