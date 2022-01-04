from tools.logger import log_info

def prompt_yesno_question(question: str) -> bool:
    prompt = "\n> " + question + " (yes/no): "
    value = input(prompt)
    while (value.strip() != 'yes' and value.strip() != 'no'):
        value = input(prompt)
    log_info("[USER-PROMPT] "+prompt.strip())
    log_info("[USER-ANSWER] "+value)
    return value == 'yes'
