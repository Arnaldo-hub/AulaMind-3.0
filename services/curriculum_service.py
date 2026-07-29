# ==========================================================
# AulaMind Enterprise 3.0
# services/curriculum_service.py
# ==========================================================

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


# ==========================================================
# LOGGING
# ==========================================================

logging.basicConfig(

    level=logging.INFO,

    format="[%(levelname)s] %(message)s"

)

logger = logging.getLogger("CurriculumService")


# ==========================================================
# CURRICULUM SERVICE
# ==========================================================

class CurriculumService:

    """
    Motor Curricular AulaMind

    Lee automáticamente todos los JSON ubicados en:

        data_curricular/

    y construye los índices:

        Curso
            ↓
        Asignatura
            ↓
        Unidad
            ↓
        Objetivos de Aprendizaje
    """

    # ======================================================
    # CONSTRUCTOR
    # ======================================================

    def __init__(self):

        logger.info("Inicializando CurriculumService...")

        self.root = Path(__file__).resolve().parent.parent

        self.data_folder = self.find_curriculum_folder()

        logger.info(

            f"Curriculum: {self.data_folder}"

        )

        # --------------------------------------------------

        self.files = []

        self.raw_data = []

        # --------------------------------------------------

        self.courses = {}

        self.subjects = defaultdict(dict)

        self.units = defaultdict(

            lambda: defaultdict(dict)

        )

        self.learning_objectives = defaultdict(

            lambda:

            defaultdict(

                lambda:

                defaultdict(list)

            )

        )

        # --------------------------------------------------

        self.stats = {

            "json": 0,

            "courses": 0,

            "subjects": 0,

            "units": 0,

            "oa": 0

        }

        # --------------------------------------------------

        self.load()


    # ======================================================
    # ENCONTRAR DATA_CURRICULAR
    # ======================================================

    def find_curriculum_folder(self):

        """
        Busca automáticamente la carpeta
        data_curricular.
        """

        candidates = list(

            self.root.rglob("data_curricular")

        )

        if not candidates:

            raise Exception(

                "No existe la carpeta data_curricular"

            )

        return candidates[0]


    # ======================================================
    # CARGAR
    # ======================================================

    def load(self):

        logger.info(

            "Buscando archivos JSON..."

        )

        self.files = sorted(

            self.data_folder.rglob("*.json")

        )

        self.stats["json"] = len(

            self.files

        )

        logger.info(

            f"{len(self.files)} JSON encontrados."

        )

        if len(self.files) == 0:

            raise Exception(

                "No existen archivos JSON."

            )

        self.raw_data.clear()

        for file in self.files:
         self.load_json(file)

        logger.info(
            f"{len(self.raw_data)} documentos cargados."
        )

        self.build_indexes()

        self.print_statistics()

    # ======================================================
    # CARGAR JSON
    # ======================================================

    def load_json(self, path: Path):

        try:

            with open(

                path,

                "r",

                encoding="utf-8",

                errors="ignore"

            ) as file:

                data = json.load(file)

        except Exception as ex:

            logger.warning(

                f"No fue posible leer {path.name}"

            )

            logger.warning(ex)

            return

        # ----------------------------------------------

        if not isinstance(

            data,

            dict

        ):

            return

        # ----------------------------------------------

        data["_file"] = path.name

        data["_folder"] = path.parent.name

        self.raw_data.append(data)
         

    # ======================================================
    # LIMPIAR TEXTO
    # ======================================================

    @staticmethod
    def clean(text):

        if text is None:

            return ""

        return str(text).strip()


        # ======================================================
    # NORMALIZAR CURSO
    # ======================================================

    @staticmethod
    def normalize_course(course):
        import re

        if not course:
            return ""

        text = str(course).lower().strip()

        text = text.replace("_", " ")
        text = text.replace("medio", " medio")
        text = text.replace("básico", " básico")
        text = text.replace("basico", " básico")
        text = text.replace("bás", " básico")
        text = text.replace("bas", " básico")

        # Normalizar 1° básico
        m = re.search(r"([1-8])\s*°?\s*básico", text)
        if m:
            return f"{m.group(1)}° Básico"

        # Normalizar 1° medio
        m = re.search(r"([1-4])\s*°?\s*medio", text)
        if m:
            return f"{m.group(1)}° Medio"

        return ""

    # ======================================================
    # CONSTRUIR ÍNDICES
    # ======================================================

    def build_indexes(self):
        """
        Construye todos los índices curriculares.
        """

        logger.info("Construyendo índices curriculares...")

        self.courses.clear()
        self.subjects.clear()
        self.units.clear()
        self.learning_objectives.clear()

        total_courses = set()
        total_subjects = set()
        total_units = 0
        total_oa = 0

        for document in self.raw_data:
            try:
                subject = self.clean(document.get("asignatura"))
                course = self.normalize_course(self.clean(document.get("curso")))

                if course == "" or subject == "":
                    continue

                total_courses.add(course)
                total_subjects.add(subject)

                # Curso
                self.courses[course] = {"id": course, "name": course}

                # Asignatura
                self.subjects[course][subject] = {"id": subject, "name": subject}

                # Unidades
                for unit in document.get("unidades", []):
                    unit_name = self.clean(unit.get("nombre"))
                    if unit_name == "":
                        continue

                    # Normalizar para evitar duplicados por espacios
                    unit_key = " ".join(unit_name.split())

                    if unit_key not in self.units[course][subject]:
                        self.units[course][subject][unit_key] = {
                            "id": unit_key,
                            "name": unit_key
                        }
                        total_units += 1

                    # OA
                    for oa in unit.get("oa", []):
                        code = self.clean(oa.get("codigo"))
                        description = self.clean(oa.get("descripcion"))

                        if code == "":
                            continue

                        # Evitar OA duplicados en la misma unidad
                        existing_codes = [
                            obj.get("code") for obj in
                            self.learning_objectives[course][subject][unit_key]
                        ]

                        if code not in existing_codes:
                            self.learning_objectives[course][subject][unit_key].append({
                                "code": code,
                                "description": description
                            })
                            total_oa += 1

            except Exception as ex:
                logger.warning(ex)

        self.stats["courses"] = len(total_courses)
        self.stats["subjects"] = len(total_subjects)
        self.stats["units"] = total_units
        self.stats["oa"] = total_oa

        logger.info(f"Cursos: {self.stats['courses']}")
        logger.info(f"Asignaturas: {self.stats['subjects']}")
        logger.info(f"Unidades: {self.stats['units']}")
        logger.info(f"OA: {self.stats['oa']}")

    # ======================================================
    # CURSOS
    # ======================================================

    def get_courses(self):
        """
        Devuelve todos los cursos ordenados.
        """

        order = [
            "1° Básico", "2° Básico", "3° Básico", "4° Básico",
            "5° Básico", "6° Básico", "7° Básico", "8° Básico",
            "1° Medio", "2° Medio", "3° Medio", "4° Medio"
        ]

        courses = list(self.courses.keys())

        def sort_key(value):
            if value in order:
                return order.index(value)
            return 999

        courses.sort(key=sort_key)
        return courses


    # ======================================================
    # ASIGNATURAS
    # ======================================================

    def get_subjects(
        self,
        course
    ):

        if course not in self.subjects:

            return []

        subjects = list(

            self.subjects[course].keys()

        )

        subjects.sort()

        return subjects


    # ======================================================
    # UNIDADES
    # ======================================================

    def get_units(

        self,

        course,

        subject

    ):

        if course not in self.units:

            return []

        if subject not in self.units[course]:

            return []

        units = list(

            self.units[course][subject].keys()

        )

        units.sort()

        return units


    # ======================================================
    # OA
    # ======================================================

    def get_learning_objectives(

        self,

        course,

        subject,

        unit

    ):

        if course not in self.learning_objectives:

            return []

        if subject not in self.learning_objectives[course]:

            return []

        if unit not in self.learning_objectives[course][subject]:

            return []

        return self.learning_objectives[

            course

        ][

            subject

        ][

            unit

        ]


    # ======================================================
    # CURSO EXISTE
    # ======================================================

    def exists_course(

        self,

        course

    ):

        return course in self.courses


    # ======================================================
    # ASIGNATURA EXISTE
    # ======================================================

    def exists_subject(

        self,

        course,

        subject

    ):

        if course not in self.subjects:

            return False

        return subject in self.subjects[course]


    # ======================================================
    # UNIDAD EXISTE
    # ======================================================

    def exists_unit(

        self,

        course,

        subject,

        unit

    ):

        if course not in self.units:

            return False

        if subject not in self.units[course]:

            return False

        return unit in self.units[course][subject]


    # ======================================================
    # OA POR CÓDIGO
    # ======================================================

    def get_objective_by_code(

        self,

        course,

        subject,

        unit,

        code

    ):

        objectives = self.get_learning_objectives(

            course,

            subject,

            unit

        )

        for objective in objectives:

            if objective.get(

                "code"

            ) == code:

                return objective

        return None


    # ======================================================
    # TOTAL OA
    # ======================================================

    def total_learning_objectives(self):

        total = 0

        for course in self.learning_objectives:

            for subject in self.learning_objectives[course]:

                for unit in self.learning_objectives[course][subject]:

                    total += len(

                        self.learning_objectives[

                            course

                        ][

                            subject

                        ][

                            unit

                        ]

                    )

        return total


    # ======================================================
    # TOTAL UNIDADES
    # ======================================================

    def total_units(self):

        total = 0

        for course in self.units:

            for subject in self.units[course]:

                total += len(

                    self.units[

                        course

                    ][

                        subject

                    ]

                )

        return total


    # ======================================================
    # TOTAL CURSOS
    # ======================================================

    def total_courses(self):

        return len(

            self.courses

        )


    # ======================================================
    # TOTAL ASIGNATURAS
    # ======================================================

    def total_subjects(self):

        total = 0

        for course in self.subjects:

            total += len(

                self.subjects[course]

            )

        return total
            # ======================================================
    # BUSCAR CURSOS
    # ======================================================

    def search_courses(self, text):

        text = self.clean(text).lower()

        if not text:
            return self.get_courses()

        return [

            course

            for course in self.get_courses()

            if text in course.lower()

        ]


    # ======================================================
    # BUSCAR ASIGNATURAS
    # ======================================================

    def search_subjects(self, course, text):

        text = self.clean(text).lower()

        return [

            subject

            for subject in self.get_subjects(course)

            if text in subject.lower()

        ]


    # ======================================================
    # BUSCAR UNIDADES
    # ======================================================

    def search_units(self, course, subject, text):

        text = self.clean(text).lower()

        return [

            unit

            for unit in self.get_units(

                course,

                subject

            )

            if text in unit.lower()

        ]


    # ======================================================
    # BUSCAR OA
    # ======================================================

    def search_learning_objectives(

        self,

        course,

        subject,

        text

    ):

        text = self.clean(text).lower()

        results = []

        for unit in self.get_units(

            course,

            subject

        ):

            objectives = self.get_learning_objectives(

                course,

                subject,

                unit

            )

            for objective in objectives:

                content = (

                    objective.get(

                        "code",

                        ""

                    )

                    + " "

                    + objective.get(

                        "description",

                        ""

                    )

                ).lower()

                if text in content:

                    item = dict(objective)

                    item["unit"] = unit

                    results.append(item)

        return results


    # ======================================================
    # CONTEXTO PLANNING
    # ======================================================

    def get_planning_context(

        self,

        course,

        subject,

        unit,

        selected_codes

    ):

        objectives = self.get_learning_objectives(

            course,

            subject,

            unit

        )

        selected = []

        selected_codes = set(selected_codes)

        for objective in objectives:

            if objective.get("code") in selected_codes:

                selected.append(objective)

        return {

            "course": course,

            "subject": subject,

            "unit": unit,

            "learning_objectives": selected,

            "total": len(selected)

        }


    # ======================================================
    # CONTEXTO EVALUATION
    # ======================================================

    def get_evaluation_context(

        self,

        course,

        subject,

        unit,

        selected_codes

    ):

        context = self.get_planning_context(

            course,

            subject,

            unit,

            selected_codes

        )

        context["evaluation"] = True

        return context


    # ======================================================
    # CONSTRUIR PROMPT IA
    # ======================================================

    def build_prompt(

        self,

        course,

        subject,

        unit,

        selected_codes

    ):

        context = self.get_planning_context(

            course,

            subject,

            unit,

            selected_codes

        )

        prompt = f"""

Eres un docente experto del MINEDUC Chile.

Genera una planificación profesional.

Curso:
{course}

Asignatura:
{subject}

Unidad:
{unit}

Objetivos de Aprendizaje:

"""

        for objective in context["learning_objectives"]:

            prompt += f"""

{objective.get('code')}

{objective.get('description')}

"""

        prompt += """

La planificación debe contener:

- Objetivo de la clase
- Inicio
- Desarrollo
- Cierre
- Recursos
- Evaluación
- Indicadores
- Adecuaciones Curriculares
- Actividades del docente
- Actividades del estudiante

Responder en formato Markdown.

"""

        return prompt.strip()


    # ======================================================
    # EXPORTAR ESTRUCTURA
    # ======================================================

    def export(self):

        return {

            "courses": self.courses,

            "subjects": self.subjects,

            "units": self.units,

            "learning_objectives":

                self.learning_objectives

        }


    # ======================================================
    # HEALTH
    # ======================================================

    def health(self):

        return {

            "loaded": True,

            "json": self.stats["json"],

            "courses": self.total_courses(),

            "subjects": self.total_subjects(),

            "units": self.total_units(),

            "learning_objectives":

                self.total_learning_objectives()

        }
            # ======================================================
    # VERIFICAR INTEGRIDAD
    # ======================================================

    def verify(self):
        """
        Verifica que el currículum se haya cargado correctamente.
        """

        errors = []

        if self.total_courses() == 0:
            errors.append("No existen cursos.")

        if self.total_subjects() == 0:
            errors.append("No existen asignaturas.")

        if self.total_units() == 0:
            errors.append("No existen unidades.")

        if self.total_learning_objectives() == 0:
            errors.append("No existen Objetivos de Aprendizaje.")

        return {

            "success": len(errors) == 0,

            "errors": errors

        }


    # ======================================================
    # RECARGAR CURRÍCULUM
    # ======================================================

    def reload(self):
        """
        Recarga completamente el currículum.
        """

        logger.info("=" * 60)
        logger.info("Recargando Currículum...")
        logger.info("=" * 60)

        self.raw_data.clear()

        self.files.clear()

        self.courses.clear()

        self.subjects.clear()

        self.units.clear()

        self.learning_objectives.clear()

        self.load()

        return self.statistics()


    # ======================================================
    # ESTADÍSTICAS COMPLETAS
    # ======================================================

    def full_statistics(self):

        return {

            "json_files":

                self.stats["json"],

            "courses":

                self.total_courses(),

            "subjects":

                self.total_subjects(),

            "units":

                self.total_units(),

            "learning_objectives":

                self.total_learning_objectives(),

            "folder":

                str(self.data_folder)

        }


    # ======================================================
    # IMPRIMIR ESTADÍSTICAS
    # ======================================================

    def print_statistics(self):

        logger.info("")

        logger.info("=" * 60)

        logger.info("CURRICULUM SERVICE")

        logger.info("=" * 60)

        logger.info(

            f"Carpeta : {self.data_folder}"

        )

        logger.info(

            f"JSON : {self.stats['json']}"

        )

        logger.info(

            f"Cursos : {self.total_courses()}"

        )

        logger.info(

            f"Asignaturas : {self.total_subjects()}"

        )

        logger.info(

            f"Unidades : {self.total_units()}"

        )

        logger.info(

            f"OA : {self.total_learning_objectives()}"

        )

        logger.info("=" * 60)

        logger.info("")


    # ======================================================
    # INFORMACIÓN
    # ======================================================

    def info(self):

        return {

            "version": "3.1",

            "engine": "CurriculumService",

            "statistics":

                self.full_statistics()

        }


    # ======================================================
    # REPRESENTACIÓN
    # ======================================================

    def __repr__(self):

        return (

            f"<CurriculumService "

            f"courses={self.total_courses()} "

            f"subjects={self.total_subjects()} "

            f"units={self.total_units()} "

            f"oa={self.total_learning_objectives()}>"

        )


# ==========================================================
# INSTANCIA GLOBAL
# ==========================================================

curriculum_service = CurriculumService()


# ==========================================================
# EXPORTACIÓN
# ==========================================================

__all__ = [

    "CurriculumService",

    "curriculum_service"

]


# ==========================================================
# FIN DEL ARCHIVO
# ==========================================================