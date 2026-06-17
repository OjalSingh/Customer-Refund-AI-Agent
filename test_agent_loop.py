from agent.agent_loop import run_loop


state = {
    "user_id": "U001",
    "user": None,
    "transactions": [],
    "policy": None
}

final_state = run_loop(state)

print("\nFINAL STATE")
print(final_state)