from pathlib import Path

from services.curriculum_adapters.tp import TPAdapter

adapter = TPAdapter()

data = {
    "modalidad": "Formación Diferenciada Técnico-Profesional",
    "sector": "Administración",
    "especialidad": "Administración",
    "curso": "3° medio TP",
    "plan": "Plan común",
    "modulos": [
        {
            "codigo": "AD-01",
            "nombre": "Proceso administrativo",
            "oa_asociados": ["OA 1", "OA 2"],
        }
    ],
}

assert adapter.can_handle(
    Path("especialidades_tp/administracion.json"),
    data,
)

records = adapter.adapt(
    Path("administracion.json"),
    data,
)

assert len(records) == 1
assert records[0]["modalidad"] == "tp"
assert records[0]["curso"] == "3° medio TP"
assert records[0]["asignatura"] == "Administración"
assert len(records[0]["unidades"]) == 1

print("TPAdapter OK")