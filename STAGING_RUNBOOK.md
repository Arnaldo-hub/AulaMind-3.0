# AulaMind — Runbook de staging

Este bloque no modifica pantallas, IA ni currículo.

## Local SQLite
1. Activar el entorno virtual.
2. `python manage_db.py bootstrap`
3. `alembic stamp 20260708_01` solo para una SQLite existente creada con `create_all` y que aún no tenga `alembic_version`.
4. `python tests/persistence_integrity.py`
5. `python staging_preflight.py`

## PostgreSQL staging nuevo
1. Configurar `DATABASE_URL`, `SECRET_KEY`, `OPENAI_API_KEY`, `DEBUG=False` y `STAGING=1` en el host.
2. Ejecutar `alembic upgrade head` sobre la base vacía.
3. Ejecutar `python staging_preflight.py`.
4. Arrancar con el comando del `Procfile`.
5. Probar `/health`, registro/login, una planificación y una evaluación.
6. Ejecutar `python tests/persistence_integrity.py` con la misma `DATABASE_URL` de staging.

## Criterio de aceptación
- conexión PostgreSQL correcta;
- migraciones en `20260708_01`;
- documentos, generaciones IA y eventos de uso aumentan al generar;
- estadísticas del Panel Principal coinciden con documentos persistidos;
- no existen generaciones ni exportaciones huérfanas.

## Estado de exportaciones
La tabla `exports` y su modelo existen, pero las rutas actuales de exportación de Evaluation siguen siendo placeholders. No se declara este punto como terminado hasta conectar Word/PDF al registro de exportaciones.
