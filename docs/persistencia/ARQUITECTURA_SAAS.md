# Núcleo de Persistencia SaaS — Semana 1

## Implementado
- `documents`: documento pedagógico común y versionable.
- `ai_generations`: trazabilidad de generaciones IA.
- `exports`: trazabilidad de exportaciones.
- `usage_events`: medición de consumo por usuario, colegio y función.
- Planning persiste una generación exitosa.
- Evaluation persiste una generación exitosa.
- Dashboard lee contadores reales desde `documents`.
- Alembic incorporado para SQLite y PostgreSQL.

## Decisión curricular
Los JSON curriculares no se modifican ni se migran en este bloque.

## Baseline de migraciones
Semana 1 usa un bootstrap controlado y luego `alembic stamp 20260708_01`, preservando la SQLite existente. Desde ese punto, toda evolución del esquema se hará mediante Alembic.
