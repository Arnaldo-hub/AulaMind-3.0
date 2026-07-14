"""
===========================================================
AulaMind Enterprise 3.0

Prueba automática
Evaluation Engine 4.0

Semana 4.1C
===========================================================
"""

from services.curriculum_engine_v4 import curriculum_engine_v4
from services.planning.evaluations import evaluation_engine


def main():

    print("=" * 60)
    print("AulaMind Enterprise 3.0")
    print("Evaluation Engine Test")
    print("=" * 60)

    record = curriculum_engine_v4.record(
        "regular",
        "1° básico",
        "Artes Visuales",
    )

    assert record is not None, (
        "No se encontró el registro curricular."
    )

    evaluation = evaluation_engine.generate(record)

    assert evaluation is not None

    assert "diagnostica" in evaluation
    assert "formativa" in evaluation
    assert "sumativa" in evaluation
    assert "instrumentos" in evaluation
    assert "ticket_salida" in evaluation

    print()
    print("✓ Registro curricular encontrado")
    print(
        f"Asignatura : {record['asignatura']}"
    )
    print(
        f"Curso      : {record['curso']}"
    )
    print(
        f"Modalidad  : {record['modalidad']}"
    )
    print()

    print(
        "Instrumentos generados:"
    )

    for instrumento in evaluation["instrumentos"]:

        print(
            f"  • {instrumento['nombre']}"
        )

    print()

    print(
        "Indicadores Formativos:"
    )

    indicadores = (
        evaluation["formativa"]
        .get("indicadores", [])
    )

    print(
        f"  Total: {len(indicadores)}"
    )

    print()

    print(
        "Preguntas Ticket de Salida:"
    )

    for pregunta in (
        evaluation["ticket_salida"]["preguntas"]
    ):

        print(
            f"  - {pregunta}"
        )

    print()

    print("=" * 60)
    print("Evaluation Engine OK")
    print("=" * 60)


if __name__ == "__main__":
    main()