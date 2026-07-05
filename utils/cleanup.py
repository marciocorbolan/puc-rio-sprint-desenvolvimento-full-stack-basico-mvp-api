# --- Bibliotecas de Terceiros ---
from datetime import datetime, timedelta, timezone

# --- Módulos do Projeto ---
from database import db
from config import JWT_BLACKLIST_EXPIRATION_HOURS


def clean_expired_tokens():
    """Remove tokens expirados da blacklist"""

    # Importação (lazy import) para evitar loop na importação
    from models.token_blacklist import TokenBlacklist
    
    cutoff = datetime.now(timezone.utc) - timedelta(hours=JWT_BLACKLIST_EXPIRATION_HOURS + 1)
    
    deleted = TokenBlacklist.query.filter(TokenBlacklist.created_at < cutoff).delete()
    db.session.commit()
    
    print(f"[Cleanup] {deleted} tokens expirados removidos da blacklist.")