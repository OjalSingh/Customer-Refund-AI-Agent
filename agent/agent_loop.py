from agent.planner import plan_next_action
from agent.executor import execute_action


def run_loop(state):

    for step in range(5):

        action = plan_next_action(state)

        print(f"\nSTEP {step+1}")
        print("ACTION:", action)

        if action["action"] == "finish":
            break

        state = execute_action(
            action,
            state
        )

    return state