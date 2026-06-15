from agent.support_agent import investigate_refund

user_id = input("Enter User ID: ")

result = investigate_refund(user_id)

print("\nFINAL DECISION")
print(result)