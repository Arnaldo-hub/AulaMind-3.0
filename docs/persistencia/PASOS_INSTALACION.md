# Instalación del núcleo SaaS

## Base local existente
1. Activar `venv`.
2. `pip install -r requirements.txt`
3. `python manage_db.py bootstrap`
4. `alembic stamp 20260708_01`
5. `python manage_db.py info`
6. `python app.py`

El bootstrap usa `create_all()` solamente como transición de consolidación: conserva tablas y datos existentes y crea las tablas SaaS ausentes. `alembic stamp` registra el baseline sin recrear tablas.

## PostgreSQL staging nuevo
1. Configurar `DATABASE_URL`.
2. `python manage_db.py bootstrap`
3. `alembic stamp 20260708_01`
4. Arrancar con `gunicorn app:app`.

A partir del baseline `20260708_01`, los cambios posteriores deben entrar como revisiones Alembic y no mediante cambios manuales de base de datos.

## Verificación
- `python manage_db.py info`
- Deben existir: `documents`, `ai_generations`, `exports`, `usage_events`, además de las tablas actuales.
- Generar una planificación real.
- Generar una evaluación real.
- Volver al Dashboard y comprobar que los contadores aumentan.
