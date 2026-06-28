import re

def slugify(text):
    if not text:
        return ""
    # Converte para minúsculo e remove espaços nas pontas
    text = text.lower().strip()
    # Substitui qualquer caractere não alfanumérico por hífen
    return re.sub(r'[\W_]+', '-', text)