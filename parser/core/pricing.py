PRICING = {
    "gpt-4o-mini": {
        "input": 0.150 / 1_000_000,  # $0.150 per 1M input tokens
        "output": 0.600 / 1_000_000, # $0.600 per 1M output tokens
    },
    "gpt-4o-2024-08-06": {
        "input": 2.5 / 1_000_000,  # $2.5 per 1M input tokens
        "output": 10 / 1_000_000, # $10 per 1M output tokens
    },
    "gemini-1.5-flash": {
        "input": 0.075 / 1_000_000,  # $0.075 per 1M input tokens
        "output": 0.30 / 1_000_000, # $0.30 per 1M output tokens
    },
    "Llama3.1 8B": {
        "input": 0 ,  # Free
        "output": 0 , # Free
    },
    "Groq Llama3.1 70b": {
        "input": 0 ,  # Free
        "output": 0 , # Free
    },
    "deepseek-chat":{
        "input": 0.0518/1_000_000, # assuming 70% cache hit
        "output": 0.28/1_000_000,
    },
    "deepseek-reasoner":{
        "input":0.2632/1_000_000, 
        "output":2.19/1_000_000,
    }
    # Add other models and their prices here if needed
}
