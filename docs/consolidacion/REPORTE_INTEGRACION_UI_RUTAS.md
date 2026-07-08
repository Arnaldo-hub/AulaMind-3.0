# Semana 1 — Integración UI y rutas

Correcciones realizadas:
- curriculum.html creado y ruta /curriculum/ validada.
- curriculum_dashboard.html creado para evitar TemplateNotFound en /curriculum/dashboard.
- evaluation.css creado e integrado con el layout base.
- evaluation.js creado para eliminar referencia estática faltante.
- /evaluation/ ahora redirige a /auth/login cuando no hay sesión, igual que los otros módulos protegidos.
- dashboard.css corregido: se eliminó el doble desplazamiento horizontal causado por grid + margin-left.
- profile.html creado para cerrar referencia de template faltante.
- sesión de autenticación armonizada agregando user_email además de email.

Validaciones ejecutadas en entorno limpio:
- instalación desde requirements.txt: OK
- importación de app: OK
- compilación Python: OK
- referencias a templates: 0 faltantes
- referencias static CSS/JS: 0 faltantes
- /health: 200
- /: 200
- /auth/login: 200
- /planning/ sin sesión: 302 a /auth/login
- /curriculum/ sin sesión: 302 a /auth/login
- /evaluation/ sin sesión: 302 a /auth/login
- /planning/ con sesión de prueba: 200
- /curriculum/ con sesión de prueba: 200
- /evaluation/ con sesión de prueba: 200
- /curriculum/dashboard con sesión de prueba: 200

Pendiente deliberadamente fuera de este parche:
- normalización Curriculum Engine 4.0
- exportadores Word/PDF
- nuevas funcionalidades docentes
- PostgreSQL staging
