# --- Bibliotecas de Terceiros ---
from datetime import datetime, timedelta

# --- Módulos do Projeto ---
from database import db
from models.token_blacklist import TokenBlacklist
from config import JWT_BLACKLIST_EXPIRATION_HOURS


def clean_expired_tokens():
    """Remove tokens expirados da blacklist"""
    cutoff = datetime.utcnow() - timedelta(hours=JWT_BLACKLIST_EXPIRATION_HOURS + 1)
    
    deleted = TokenBlacklist.query.filter(TokenBlacklist.created_at < cutoff).delete()
    db.session.commit()
    
    print(f"[Cleanup] {deleted} tokens expirados removidos da blacklist.")