from llm import ask_llm

print("Sending request...")

response = ask_llm(
    "Say hello in one short sentence."
)

print("\nResponse:")
print(response)