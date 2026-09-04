# routes/curriculum_data.py
# Fuente de verdad hardcodeada. No depende del CurriculumService.
# Basada en el currículum chileno actual.

COURSE_SUBJECTS = {
    "1° Básico": [
        "Artes Visuales",
        "Ciencias Naturales",
        "Educación Física y Salud",
        "Historia, Geografía y Ciencias Sociales",
        "Lengua y Cultura de los Pueblos Originarios Ancestrales",
        "Lenguaje y Comunicación",  # ← CORREGIDO: no "Lenguaje y Literatura"
        "Matemáticas",              # ← CORREGIDO: plural en básica
        "Música",
        "Orientación",
        "Religión Católica",
        "Religión Evangélica",
        "Tecnología"
    ],
    "2° Básico": [
        "Artes Visuales",
        "Ciencias Naturales",
        "Educación Física y Salud",
        "Historia, Geografía y Ciencias Sociales",
        "Lengua y Cultura de los Pueblos Originarios Ancestrales",
        "Lenguaje y Comunicación",
        "Matemáticas",
        "Música",
        "Orientación",
        "Religión Católica",
        "Religión Evangélica",
        "Tecnología"
    ],
    "3° Básico": [
        "Artes Visuales",
        "Ciencias Naturales",
        "Educación Física y Salud",
        "Historia, Geografía y Ciencias Sociales",
        "Lengua y Cultura de los Pueblos Originarios Ancestrales",
        "Lenguaje y Comunicación",
        "Matemáticas",
        "Música",
        "Orientación",
        "Religión Católica",
        "Religión Evangélica",
        "Tecnología"
    ],
    "4° Básico": [
        "Artes Visuales",
        "Ciencias Naturales",
        "Educación Física y Salud",
        "Historia, Geografía y Ciencias Sociales",
        "Lengua y Cultura de los Pueblos Originarios Ancestrales",
        "Lenguaje y Comunicación",
        "Matemáticas",
        "Música",
        "Orientación",
        "Religión Católica",
        "Religión Evangélica",
        "Tecnología"
    ],
    "5° Básico": [
        "Artes Visuales",
        "Ciencias Naturales",
        "Educación Física y Salud",
        "Historia, Geografía y Ciencias Sociales",
        "Inglés",  # ← Aparece desde 5°
        "Lengua y Cultura de los Pueblos Originarios Ancestrales",
        "Lenguaje y Comunicación",
        "Matemáticas",
        "Música",
        "Orientación",
        "Religión Católica",
        "Religión Evangélica",
        "Tecnología"
    ],
    "6° Básico": [
        "Artes Visuales",
        "Ciencias Naturales",
        "Educación Física y Salud",
        "Historia, Geografía y Ciencias Sociales",
        "Inglés",
        "Lengua y Cultura de los Pueblos Originarios Ancestrales",
        "Lenguaje y Comunicación",
        "Matemáticas",
        "Música",
        "Orientación",
        "Religión Católica",
        "Religión Evangélica",
        "Tecnología"
    ],
    "7° Básico": [
        "Artes Visuales",
        "Ciencias Naturales",
        "Educación Física y Salud",
        "Historia, Geografía y Ciencias Sociales",
        "Inglés",
        "Lengua y Cultura de los Pueblos Originarios Ancestrales",
        "Lengua y Literatura",  # ← Cambia desde 7°
        "Matemáticas",
        "Música",
        "Orientación",
        "Religión Católica",
        "Religión Evangélica",
        "Tecnología"
    ],
    "8° Básico": [
        "Artes Visuales",
        "Ciencias Naturales",
        "Educación Física y Salud",
        "Historia, Geografía y Ciencias Sociales",
        "Inglés",
        "Lengua y Cultura de los Pueblos Originarios Ancestrales",
        "Lengua y Literatura",
        "Matemáticas",
        "Música",
        "Orientación",
        "Religión Católica",
        "Religión Evangélica",
        "Tecnología"
    ],
    "I° Medio": [
        "Artes Visuales",
        "Biología",
        "Ciencias Naturales",  # o Física/Química según cómo lo tengas
        "Educación Física y Salud",
        "Historia, Geografía y Ciencias Sociales",
        "Inglés",
        "Lengua y Literatura",
        "Matemáticas",
        "Música",
        "Orientación",
        "Religión Católica",
        "Religión Evangélica",
        "Tecnología"
    ],
    "II° Medio": [
        "Artes Visuales",
        "Biología",
        "Educación Física y Salud",
        "Física",
        "Historia, Geografía y Ciencias Sociales",
        "Inglés",
        "Lengua y Literatura",
        "Matemáticas",
        "Música",
        "Orientación",
        "Química",
        "Religión Católica",
        "Religión Evangélica",
        "Tecnología"
    ],
    "III° Medio": [
        "Artes Visuales",
        "Biología",
        "Educación Física y Salud",
        "Física",
        "Historia, Geografía y Ciencias Sociales",
        "Inglés",
        "Lengua y Literatura",
        "Matemáticas",
        "Música",
        "Orientación",
        "Química",
        "Religión Católica",
        "Religión Evangélica",
        "Tecnología"
    ],
    "IV° Medio": [
        "Artes Visuales",
        "Biología",
        "Educación Física y Salud",
        "Física",
        "Historia, Geografía y Ciencias Sociales",
        "Inglés",
        "Lengua y Literatura",
        "Matemáticas",
        "Música",
        "Orientación",
        "Química",
        "Religión Católica",
        "Religión Evangélica",
        "Tecnología"
    ]
}

def get_subjects_for_course(course_name: str):
    """Devuelve las asignaturas para un curso. No toca el singleton."""
    # Normalizar el nombre del curso (por si viene con espacios raros o sin °)
    normalized = course_name.strip()
    subjects = COURSE_SUBJECTS.get(normalized)
    if subjects:
        return sorted(subjects)
    return None