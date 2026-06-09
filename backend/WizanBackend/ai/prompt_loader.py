# backend/ai/prompt_loader.py
import yaml
from pathlib import Path

def load_prompt(agent_name: str, version: str = "v1") -> dict:
    path = Path(f"prompts/{version}/{agent_name}.yaml")
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# usage anywhere in the codebase:
# prompt = load_prompt("cognitive_agent")
# system_msg = prompt["system"].format(score=75)