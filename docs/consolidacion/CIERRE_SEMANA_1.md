# Cierre técnico — Semana 1: Consolidación

## Decisión de arquitectura

AulaMind-3.0 es la única base de código y runtime del producto. Copiloto Docente queda únicamente como fuente histórica de activos reutilizables y no como segunda aplicación en ejecución.

## Estado verificado

- Rama de trabajo: `consolidation`.
- Repositorio remoto único de AulaMind-3.0.
- Arranque local validado.
- Staging desplegado y operativo.
- PostgreSQL adoptado como motor definitivo para staging y producción.
- SQLite conservado para desarrollo local.
- Endpoint `/health` validado remotamente.
- Registro, login, logout y reingreso validados.
- Planning y Evaluation validados en staging.
- Persistencia de documentos validada entre sesiones.
- Dashboard conectado a estadísticas persistentes.
- Corrección visual del dashboard desplegada.
- Estructura curricular congelada durante la consolidación.

## Alcance posterior

Actividad reciente real, historial documental, edición de documentos existentes, exportación Word/PDF, trazabilidad de exportaciones y prueba integral del ciclo documental pasan al bloque funcional posterior.

## Criterio de aceptación

Cumplido: AulaMind inicia localmente y en staging desde una única base de código, con instalación y arranque funcionales, autenticación operativa y sin dependencia de Copiloto Docente como segunda aplicación.

**Estado final: SEMANA 1 CERRADA Y APROBADA.**
