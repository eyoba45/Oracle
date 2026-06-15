from agent.core import run_agent

print("🔮 Oracle AI Agent")
print("=" * 50)
print("Ask me anything. I will search the web for you.")
print("Type 'exit' to quit\n")

while True:
    question = input("You: ").strip()
    
    if question.lower() == "exit":
        print("Goodbye!")
        break
    
    if not question:
        continue
    
    print("\n🤔 Oracle is thinking...\n")
    
    result = run_agent(question)
    
    print(f"Oracle: {result['answer']}")
    print(f"\n📊 Completed in {result['total_steps']} steps")
    print("=" * 50 + "\n")
    