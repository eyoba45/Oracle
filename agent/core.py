from groq import Groq
from dotenv import load_dotenv
from agent.prompts import SYSTEM_PROMPT
from agent.tools import TOOLS
import os
import json
import re

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def parse_tool_call(response: str):
    """
    Check if the AI wants to use a tool.
    Returns (tool_name, params) or None if no tool needed.
    """
    if "TOOL:" in response and "PARAMS:" in response:
        try:
            tool_match = re.search(r"TOOL:\s*(\w+)", response)
            params_match = re.search(r"PARAMS:\s*(\{.*\})", response, re.DOTALL)
            
            if tool_match and params_match:
                tool_name = tool_match.group(1).strip()
                params = json.loads(params_match.group(1).strip())
                return tool_name, params
        except:  # noqa: E722
            pass
    return None


def run_agent(user_message: str, max_steps: int = 10) -> dict:
    """
    The main ReAct loop.
    Keeps running until the agent gives a final answer
    or reaches the maximum number of steps.
    """
    # This stores the full conversation including tool results
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]
    
    # This stores what the agent did step by step
    steps = []
    
    for step in range(max_steps):
        # Ask the LLM what to do next
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.1,  # low temperature = more consistent tool usage
            max_tokens=1000
        )
        
        ai_message = response.choices[0].message.content
        
        # Check if the AI wants to use a tool
        tool_call = parse_tool_call(ai_message)
        
        if tool_call:
            tool_name, params = tool_call
            
            # Check if tool exists
            if tool_name not in TOOLS:
                tool_result = f"Tool '{tool_name}' does not exist."
            else:
                # Actually call the tool
                print(f"  🔧 Using tool: {tool_name} with {params}")
                tool_func = TOOLS[tool_name]
                tool_result = tool_func(**params)
            
            # Record this step
            steps.append({
                "step": step + 1,
                "action": f"Used tool: {tool_name}",
                "params": params,
                "result": tool_result[:200] + "..." if len(tool_result) > 200 else tool_result
            })
            
            # Add the tool call and result to conversation history
            messages.append({"role": "assistant", "content": ai_message})
            messages.append({
                "role": "user",
                "content": f"Tool result for {tool_name}:\n{tool_result}\n\nContinue."
            })
        
        else:
            # No tool call — this is the final answer
            steps.append({
                "step": step + 1,
                "action": "Final answer",
                "result": ai_message
            })
            
            return {
                "answer": ai_message,
                "steps": steps,
                "total_steps": step + 1
            }
    
    # If we hit max steps return whatever we have
    return {
        "answer": "I reached the maximum number of steps. Here is what I found so far: " + ai_message,
        "steps": steps,
        "total_steps": max_steps
    }