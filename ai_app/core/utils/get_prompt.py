def get_prompt(tool_name):
    file_path = f"app/core/prompts/{tool_name.lstrip('_')}.txt"
    with open(file_path, encoding="utf-8") as f:
        return f.read()