"""
===========================================================
AulaMind Enterprise 3.0
services/queue_service.py
-----------------------------------------------------------
Conexión Redis + RQ para generaciones async
===========================================================
"""

import os
from redis import Redis
from rq import Queue

from config import Config


def get_redis_url():
    """Devuelve URL Redis válida para RQ (nunca memory://)."""
    url = Config.RATELIMIT_STORAGE_URI
    if not url or url == "memory://":
        # Fallback para desarrollo local sin Redis
        return os.getenv("REDIS_URL", "redis://localhost:6379/0")
    return url


def get_queue(name="ai_generations"):
    redis_conn = Redis.from_url(get_redis_url(), socket_connect_timeout=10)
    return Queue(name, connection=redis_conn)


# Instancia global para importar rápido
queue = get_queue()