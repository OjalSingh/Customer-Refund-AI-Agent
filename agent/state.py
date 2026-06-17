class AgentState:

    def __init__(self, user_message):

            self.state = {
                "user_message": user_message,
                "intent": None,

                "customer_context": {},

                "retrieved_docs": [],
                "document_contents": {},
                "investigation_result": None,
                "explanation": None,

                "merchant": None,

                "user_id": None,
                "user": None,

                "transactions": [],
                "policy": None,

                "policy_result": None,
                "risk_result": None,

                "decision": None,

                "missing_fields": [],
                "conversation_history": [],

                "audit_log": [],
            }

    def update(self, key, value):
        self.state[key] = value

    def log(self, message):
        self.state["audit_log"].append(message)

    def value(self, key, default=None):
        return self.state.get(key, default)

    def get(self):
        return self.state
    
    def update_customer_context(self, key, value):
        if "customer_context" not in self.state:
            self.state["customer_context"] = {}

        self.state["customer_context"][key] = value