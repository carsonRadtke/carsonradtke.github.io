---
layout: post
title: "Talking to Robots: Building the Agentic Loop"
date: 2026-06-06
categories: ai
excerpt: "TODO (@carsonradtke)"
---

Building an agentic loop may be the next `print("Hello, World")`.
LLMs have gifted everyone with the ability to build, but how does your agent actually work?

The agentic loop is really quite simple: 
1. Get input from human
1. Pass human input to agent
1. Wait for agent's response

```python
SYSTEM_PROMPT = "You are an AI assistant. Be helpful!"

agent = AgenticActor(model='gemma4', system_prompt=SYSTEM_PROMPT)
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
    _context: list[dict]

    # ...

    def __init__(self, *, model, system_prompt):
        self._context.append({"role": "system", "content": system_prompt})

    def respond(self, human_input: str) -> str:
        _context.append({"role": "user", "content": human_input})
        response = self._get_response()
        _context.append({"role": "assistant", "content": response})
        return response

    # ...
```

To actually talk to the LLM, the ollama python api (ollama-python) is most convenient.

<details>
<summary>Ollama Side Quest</summary>

<!-- TODO (@carsonradtke): Installing ollama. -->

</details>

```python
class AgenticActor:
    _model: str

    # ...

    def _get_response(self) -> str:
        response = ollama.chat(self._model, messages=self._context)
        return response.message.content

    # ...
```

That's all you need for a simple chat app!
Here is a complete working example:

<details>
<summary>Basic Agent Example</summary>

```python
# TODO (@carsonradtke): simple working example
```

</details>

### Improving the Agentic Loop

The simple example is pretty cool and, with a powerful enough model, can be useful.
But the only thing the agent knows comes from the LLM's weights.
This makes the model susceptible to hallucinations.
In order to combat this, we can expose tools to the agent.

#### Tools

A helpful agent needs to be able to do the following things:
 - Access the internet
 - Search the local filesystem
 - Read local files
 - Run simple scripts

<!-- TODO (@carsonradtke): How are tools exposed to the agent? -->
<!-- TODO (@carsonradtke): How are tools written? -->
<!-- TODO (@carsonradtke): How does the agent invoke tools? -->

#### Streaming Agent Responses

In addition to the `tools` kwarg, we can also pass `strem=True`.
This provides the model with a better user experience that helps the user see what is going on.

<!-- TODO (@carsonradtke): how to stream chunks -->

#### Reasoning Models

Many new models, especially those capabale of tool calling, also have a reasoning mode.
Reasoning, or "thinking", gives the model the ability to chain thoughts together and plan out tasks.
This tends to improve agent answers and mitigate hallucinations.

<!-- TODO (@carsonradtke): `thinking=True` + example -->

### Appendix

Here is the harness that I use as my own local agent:

<!-- TODO (@carsonradtke): Once my own model is good, link there. -->

*AI Disclaimer: The article was written by a human (me); AI generated the title and summary.*
