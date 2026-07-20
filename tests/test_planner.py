"""
===========================================================
AulaMind Enterprise 3.0

Planning Engine Test

Semana 4.1H
===========================================================
"""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.planning.planner import planning_engine


def main():

    plan = planning_engine.generate(

        modalidad="regular",

        curso="1° básico",

        asignatura="Artes Visuales",

    )

    assert plan is not None

    assert "curriculum" in plan
    assert "didactics" in plan
    assert "evaluation" in plan
    assert "resources" in plan
    assert "dua" in plan
    assert "indicators" in plan
    assert "prompt" in plan
    assert "metadata" in plan

    print("=" * 60)
    print("Planning Engine OK")
    print("=" * 60)

    curriculum = plan["curriculum"]

    print()
    print("CURRICULUM")
    print("-----------------------------")
    print("Modalidad :", curriculum["modalidad"])
    print("Curso     :", curriculum["curso"])
    print("Asignatura:", curriculum["asignatura"])

    print()
    print("MÓDULOS GENERADOS")
    print("-----------------------------")

    print("Didactics :", bool(plan["didactics"]))
    print("Evaluation:", bool(plan["evaluation"]))
    print("Resources :", bool(plan["resources"]))
    print("DUA       :", bool(plan["dua"]))
    print("Indicators:", bool(plan["indicators"]))

    print()
    print("Prompt generado:", len(plan["prompt"]), "caracteres")

    print()
    print("=" * 60)
    print("PLANNING ENGINE 4.0 OK")
    print("=" * 60)


if __name__ == "__main__":
    main()