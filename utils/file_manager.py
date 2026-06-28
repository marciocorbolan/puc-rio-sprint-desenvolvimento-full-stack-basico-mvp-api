import base64
import os
import uuid

def get_image_as_base64(file_path):
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "rb") as image_file:
                # Lê o binário e converte para base64
                encoded_string = base64.b64encode(image_file.read())
                # Retorna a string decodificada (utf-8)
                return encoded_string.decode('utf-8')
        except Exception:
            return ''
    return ''

#########################################################################
    
def save_image_from_base64(image_bytes, model_name, record_id, extension='png'):
    # Define a estrutura: uploads/model_name/record_id/
    base_path = os.path.join('uploads', model_name, str(record_id))
    
    # Tenta criar o diretório
    try:
        if not os.path.exists(base_path):
            os.makedirs(base_path, exist_ok=True)
    except OSError as e:
        return None  # Ou lance uma exceção customizada

    filename = f"{uuid.uuid4().hex}.{extension}"
    file_path = os.path.join(base_path, filename)
    
    try:
        # Grava o arquivo
        with open(file_path, "wb") as f:
            f.write(image_bytes)
            f.flush() # Garante que os dados saiam do buffer do sistema
            os.fsync(f.fileno()) # Força a escrita física no disco
        
        # Validação final: verifica se o arquivo existe e tem tamanho > 0
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            return file_path
        else:
            return None
            
    except (IOError, OSError):
        # Caso ocorra falha na gravação, tenta remover lixo se existir
        if os.path.exists(file_path):
            os.remove(file_path)
        return None