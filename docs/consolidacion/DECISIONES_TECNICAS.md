# Decisiones Técnicas

Documento oficial de decisiones de arquitectura de **AulaMind Enterprise 3.0**.

Cada decisión relevante se registra con código **DT-XXX**, fecha, contexto
y justificación. Las decisiones registradas son vinculantes: ningún cambio
futuro puede contradecirlas sin crear una nueva DT que las revoque.

---

## Arquitectura vigente

Stack real de la plataforma (v3.0.0):

```
Frontend (Jinja2 + dashboard.css + JS por módulo)
        ↓
Blueprints Flask (routes/)
        ↓
Servicios de negocio (services/)
        ↓
Modelos SQLAlchemy 2.x (models/)
        ↓
SQLite (desarrollo) / PostgreSQL (producción, Render)

Motor curricular (services/curriculum_*):
data_curricular/ → 483 JSON → 12 cursos, 190 asignaturas,
496 unidades, 2389 OA
```

- **Framework**: Flask (blueprints, sesiones, Jinja2)
- **ORM**: SQLAlchemy 2.x con `SessionLocal` por request
- **Autenticación**: sesión Flask + `AuthService` (werkzeug)
- **Autorización**: `security/authorization.py`
  (`login_required`, `role_required`)
- **Migraciones**: Alembic (`migrations/versions/`)
- **Deploy**: GitHub → Render (auto-deploy)
- **Verificación**: `scripts/verify_predeploy.py`

---

## Principios

- Un archivo por vez.
- Un sprint por vez.
- Todo debe compilar.
- Todo debe probarse.
- No romper contratos.
- No modificar componentes estables.
- Mantener arquitectura modular.
- Separación estricta de responsabilidades.

---

## Registro de decisiones (DT)

### DT-001 a DT-008

Decisiones de la etapa de consolidación (Fase 1). Ver
`docs/consolidacion/DECISION_ARQUITECTURA.md` y releases
`RELEASE_1_0_0.md` / `RELEASE_1_1_0.md` para el detalle histórico.

### DT-009 — [PENDIENTE DE DOCUMENTAR]

Decisión tomada durante el cierre de los módulos M-06/M-07/M-08.
Contenido aún no traspasado al registro. **No crear DT-016 sin
completar esta entrada.**

### DT-010 — IDs como UUID strings

**Fecha**: 2026-07 · **Estado**: Vigente

Todos los identificadores son UUID strings (36 chars). Prohibido
convertirlos con `int()`. Las rutas reciben IDs como strings
(`/<document_id>`, `/<user_id>`) sin conversión de tipo.

*Contexto*: el intento de forzar `int(document_id)` por compatibilidad
con PostgreSQL rompió guías, rúbricas y evaluación (commit `4e0b834`).

### DT-011 — Eliminación lógica (soft delete)

**Fecha**: 2026-07 · **Estado**: Vigente

Ningún módulo borra físicamente entidades con historial asociado.
`DELETE /admin/api/usuarios/<id>` desactiva (`is_active=False`),
no elimina la fila.

*Justificación*: preserva planificaciones, rúbricas y documentos
generados por el usuario; permite auditoría y reactivación.

### DT-012 — Autoprotección de la cuenta administradora

**Fecha**: 2026-07 · **Estado**: Vigente

Un administrador no puede: desactivar su propia cuenta, eliminarla,
ni cambiar su propio rol a uno no-admin. La UI además oculta los
botones de toggle/eliminar sobre la cuenta propia.

*Justificación*: evita dejar la plataforma sin administradores
activos por un error de operación.

### DT-013 — Sidebar unificado en partial compartido

**Fecha**: 2026-07 · **Estado**: Vigente

El menú lateral vive en `templates/partials/sidebar_menu.html` y se
incluye con `{% set active_menu = '...' %}` + `{% include %}`.
Prohibido duplicar el menú en templates nuevos. Los ítems sin módulo
implementado no se muestran (cero enlaces `href="#"` en producción).

*Contexto*: existían 3 versiones divergentes del sidebar copiadas
a mano en ~15 templates; el dashboard tenía HTML malformado y 4
enlaces muertos.

### DT-014 — Verificador pre-deploy obligatorio

**Fecha**: 2026-07 · **Estado**: Vigente

Ningún push a la rama de despliegue se realiza sin ejecutar antes
`scripts/verify_predeploy.py` (o `verify_predeploy.ps1` en Windows)
y obtener exit code 0. El verificador chequea: sintaxis Python,
parseo Jinja2, arranque de la app, respuesta 200 de todas las
páginas, ausencia de enlaces muertos y visibilidad por rol.

### DT-015 — Email de usuario inmutable en self-service

**Fecha**: 2026-07 · **Estado**: Vigente

El usuario no puede cambiar su propio email desde el perfil (campo
de solo lectura); solo un administrador lo modifica desde M-09.

*Justificación*: el email es la identidad de login y del reseteo
de contraseña; un cambio self-service rompe ambos flujos y abre
vector de secuestro de cuenta.

---

Estas decisiones constituyen la base técnica oficial de
AulaMind Enterprise 3.0.
