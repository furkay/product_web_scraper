def remove_line_breaks_from(text: str):
    if text:
        return text.replace('\n', ' ').replace('\r', '')
    return None
