---
layout: post
title: "Talking to Robots: Building the Agentic Loop"
date: 2026-02-22
categories: ai
excerpt: "TODO (@carsonradtke)"
---
Building an agentic loop may be the next `print("Hello, World")`.
LLMs have gifted everyone with the ability to build, but how does your agent actually work?

The agentic loop is really quite simple: 
1. Get input from human
2. Pass human input to agent
3. Wait for agent's response

```python
#!/bin/env python3

SYSTEM_PROMPT = "You are an AI assistant. Be helpful!"

if __name__ == '__main__':
    agent = AgenticActor(model='qwen3:0.6b', system_prompt=SYSTEM_PROMPT)
    while True:
        human_input = input("Human: ")
        agent_response = agent.respond(human_input)
        print("Agent: {agent_response}")
```

Clearly step 2 is a bit hand-wavy.
The most important thing that the agent needs to do is to keep track of the conversation history (AKA "context").

### Context

Context is simply a collection of messages.
Each message comes from somewhere -- either the user, the agent (assistant), a tool call, or the system.

```python
class AgenticActor:
    _context: List[object]

    # ...

    def respond(self, human_input: str) -> str:
        _context.append({"role": "user", "content": human_input})
        response = self._get_response()
        _context.append({"role": "assistant", "content": response})
        return response

    # ...
```

*AI Disclaimer: The article was written by a human (me); AI generated the title and summary.*
