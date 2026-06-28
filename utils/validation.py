import base64
import imghdr

def validate_base64_image(base64_str, max_size_mb=8):
    try:
        if ',' in base64_str:
            base64_str = base64_str.split(',')[1]
        
        image_data = base64.b64decode(base64_str)
        
        # Valida tamanho
        if len(image_data) > max_size_mb * 1024 * 1024:
            return False, f"Imagem excede o limite de {max_size_mb}MB", None
            
        # Valida formato
        img_type = imghdr.what(None, h=image_data)
        if img_type not in ['jpeg', 'jpg', 'png', 'gif']:
            return False, "Formato de imagem inválido", None
            
        return True, None, image_data
    except Exception:
        return False, "Base64 inválido", None