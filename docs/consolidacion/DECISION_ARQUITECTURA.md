# Decisión de arquitectura — Semana 1

- Runtime único: AulaMind 3.0.
- Copiloto Docente no se ejecuta como segunda aplicación.
- Sus herramientas curriculares reutilizables se integran como utilidades offline en `tools/curriculum`.
- Los JSON curriculares permanecen como fuente maestra durante el plan de 90 días.
- PostgreSQL almacenará usuarios, colegios, membresías, proyectos pedagógicos, documentos, versiones, generaciones, consumo y auditoría.
- Toda llamada IA debe pasar por el servicio central de AulaMind.
- No se agregan funcionalidades nuevas durante la consolidación.
