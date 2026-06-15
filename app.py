from agent.intent_extractor import extract_intent

message = "I was charged twice by Netflix and need a refund"

print(extract_intent(message))