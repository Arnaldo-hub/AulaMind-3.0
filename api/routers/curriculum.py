"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Router

Sprint 9.6.2
===========================================================
"""

from __future__ import annotations

from fastapi import APIRouter

from api.providers.curriculum_provider import (
    curriculum_provider,
)

router = APIRouter()

# ---------------------------------------------------------
# GET /curriculum
# ---------------------------------------------------------

@router.get(
    "",
    summary="Currículo completo",
)
def get_curriculum():

    return curriculum_provider.summary()


# ---------------------------------------------------------
# GET /curriculum/modalities
# ---------------------------------------------------------

@router.get(
    "/modalities",
    summary="Modalidades",
)
def get_modalities():

    return curriculum_provider.modalities()


# ---------------------------------------------------------
# GET /curriculum/courses
# ---------------------------------------------------------

@router.get(
    "/courses",
    summary="Cursos",
)
def get_courses():

    return curriculum_provider.courses()


# ---------------------------------------------------------
# GET /curriculum/subjects
# ---------------------------------------------------------

@router.get(
    "/subjects",
    summary="Asignaturas",
)
def get_subjects():

    return curriculum_provider.subjects()


# ---------------------------------------------------------
# GET /curriculum/statistics
# ---------------------------------------------------------

@router.get(
    "/statistics",
    summary="Estadísticas",
)
def get_statistics():

    return curriculum_provider.statistics()

# ---------------------------------------------------------
# GET /curriculum/modality/{name}
# ---------------------------------------------------------

@router.get(
    "/modality/{name}",
    summary="Buscar modalidad",
)
def get_modality(name: str):

    return curriculum_provider.find_modality(name)

# ---------------------------------------------------------
# GET /curriculum/course/{name}
# ---------------------------------------------------------

@router.get(
    "/course/{name}",
    summary="Buscar curso",
)
def get_course(name: str):

    return curriculum_provider.find_course(name)

# ---------------------------------------------------------
# GET /curriculum/subject/{name}
# ---------------------------------------------------------

@router.get(
    "/subject/{name}",
    summary="Buscar asignatura",
)
def get_subject(name: str):

    return curriculum_provider.find_subject(name)

# ---------------------------------------------------------
# GET /curriculum/search/modalities
# ---------------------------------------------------------

@router.get(
    "/search/modalities",
    summary="Buscar modalidades",
)
def search_modalities(q: str):

    return curriculum_provider.search_modalities(q)

# ---------------------------------------------------------
# GET /curriculum/search/courses
# ---------------------------------------------------------

@router.get(
    "/search/courses",
    summary="Buscar cursos",
)
def search_courses(q: str):

    return curriculum_provider.search_courses(q)

# ---------------------------------------------------------
# GET /curriculum/search/subjects
# ---------------------------------------------------------

@router.get(
    "/search/subjects",
    summary="Buscar asignaturas",
)
def search_subjects(q: str):

    return curriculum_provider.search_subjects(q)