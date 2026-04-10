from functools import lru_cache
from pathlib import Path

PROMPTS_ROOT = Path(__file__).resolve().parent


@lru_cache
def load_prompt_template(relative_path: str) -> str:
    """Load and cache a prompt template from the prompts directory."""
    prompt_path = (PROMPTS_ROOT / relative_path).resolve()

    try:
        prompt_path.relative_to(PROMPTS_ROOT)
    except ValueError as exc:
        raise ValueError(f"Prompt path escapes prompt root: {relative_path}") from exc

    if not prompt_path.is_file():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")

    return prompt_path.read_text(encoding="utf-8").strip()
