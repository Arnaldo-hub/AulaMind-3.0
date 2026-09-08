"""
===========================================================
AulaMind Enterprise 3.0
services/curriculum_tp_service.py
-----------------------------------------------------------

Motor Curricular Técnico-Profesional (v3.5)

Las Bases Curriculares de Formación Diferenciada TP
definen OA TERMINALES de perfil de egreso para el ciclo
completo 3°-4° medio. No existe desglose anual oficial:
la distribución por módulos corresponde a los Programas
de Estudio (distinto documento).

Este servicio indexa data_curricular/especialidades_tp1/
y expone cursos, asignaturas y OA con la MISMA interfaz
que CurriculumService, para que la UI no distinga.

Fuente: Bases Curriculares Formación Diferenciada
Técnico-Profesional, MINEDUC.

Autor: Biotecno Chile
===========================================================
"""

import json
import logging
import re
from pathlib import Path

logger = logging.getLogger(__name__)


class CurriculumTPService:
    """
    Índice curricular para Enseñanza Media TP.
    Singleton de proceso (mismo patrón que CurriculumService).
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    # ---------------------------------------------------------
    # Cursos TP: el sector + nivel define el "curso" visible.
    # La malla TP es 3°-4° medio por especialidad.
    # ---------------------------------------------------------

    COURSE_TEMPLATE = "{nivel}° Medio TP"

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.root = Path(__file__).resolve().parent.parent
        self.data_folder = self._find_data_folder()
        self.raw_data = []
        self.courses = {}
        self.subjects = {}
        self.learning_objectives = {}
        self.load_files()
        self.build_indexes()

    def _find_data_folder(self):
        candidates = list(self.root.rglob("especialidades_tp1"))
        if not candidates:
            raise Exception("No existe la carpeta especialidades_tp1")
        return candidates[0]

    def load_files(self):
        files = sorted(self.data_folder.rglob("*.json"))
        inventario = [f for f in files if "INVENTARIO" in f.name.upper()]
        for f in files:
            if f in inventario:
                continue
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                data["_file"] = f.name
                data["_folder"] = f.parent.name
                self.raw_data.append(data)
            except Exception as ex:
                logger.warning("TP: no se pudo leer %s: %s", f.name, ex)

    @staticmethod
    def clean(text):
        return "" if text is None else str(text).strip()

    def build_indexes(self):
        """
        Normaliza cada JSON TP:
          curso    = "3° Medio TP" y "4° Medio TP" (ciclo completo)
          asignatura = especialidad (ej. "Atención de Enfermería")
          unidad   = sector (carpeta contenedora, ej. "salud_educacion")
          oa       = oa_perfil_egreso
        """
        self.courses.clear()
        self.subjects.clear()
        self.learning_objectives.clear()

        for doc in self.raw_data:
            try:
                especialidad = self.clean(doc.get("especialidad"))
                if not especialidad:
                    continue

                sector = self.clean(doc.get("_folder", ""))
                oas = doc.get("oa_perfil_egreso", []) or []

                for nivel in (3, 4):
                    curso = self.COURSE_TEMPLATE.format(nivel=nivel)

                    self.courses[curso] = {"id": curso, "name": curso}
                    self.subjects.setdefault(curso, {})
                    self.subjects[curso][especialidad] = {
                        "id": especialidad, "name": especialidad
                    }
                    self.learning_objectives.setdefault(curso, {})
                    self.learning_objectives[curso].setdefault(especialidad, {})

                    unit_key = sector
                    self.learning_objectives[curso][especialidad].setdefault(unit_key, [])

                    existing = {
                        o.get("code")
                        for o in self.learning_objectives[curso][especialidad][unit_key]
                    }
                    for oa in oas:
                        code = self.clean(oa.get("codigo"))
                        desc = self.clean(oa.get("descripcion"))
                        if not code or code in existing:
                            continue
                        self.learning_objectives[curso][especialidad][unit_key].append({
                            "code": code,
                            "description": desc,
                        })
                        existing.add(code)
            except Exception as ex:
                logger.warning("TP build_indexes: %s", ex)

    # ---------------------------------------------------------
    # Interfaz pública (misma forma que CurriculumService)
    # ---------------------------------------------------------

    def get_courses(self):
        return sorted(self.courses.values(), key=lambda c: c["name"])

    def get_subjects(self, course):
        return sorted(self.subjects.get(course, {}).values(), key=lambda s: s["name"])

    def get_units(self, course, subject):
        units = self.learning_objectives.get(course, {}).get(subject, {})
        return [{"id": u, "name": u} for u in sorted(units)]

    def get_objectives(self, course, subject, unit):
        return self.learning_objectives.get(course, {}).get(subject, {}).get(unit, [])

    def statistics(self):
        oa_total = sum(
            len(oas)
            for curso in self.learning_objectives.values()
            for subj in curso.values()
            for oas in subj.values()
        )
        return {
            "files": len(self.raw_data),
            "courses": len(self.courses),
            "subjects": sum(len(s) for s in self.subjects.values()),
            "learning_objectives": oa_total,
        }


# Singleton de proceso
curriculum_tp_service = CurriculumTPService()