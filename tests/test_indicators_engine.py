from services.curriculum_engine_v4 import curriculum_engine_v4
from services.planning.indicators import indicators_engine


def main():

    record = curriculum_engine_v4.record(
        "regular",
        "1° básico",
        "Artes Visuales",
    )

    assert record is not None

    data = indicators_engine.generate(record)

    assert data is not None

    assert "indicadores" in data
    assert "criterios_exito" in data
    assert "evidencias" in data
    assert "habilidades" in data
    assert "actitudes" in data

    print("=" * 60)
    print("Indicators Engine OK")
    print("=" * 60)

    print()

    print("Indicadores")

    for item in data["indicadores"]:
        print(" •", item["descripcion"])

    print()

    print("Criterios de éxito")

    for item in data["criterios_exito"]:
        print(" •", item)

    print()

    print("Evidencias")

    for item in data["evidencias"]:
        print(" •", item)


if __name__ == "__main__":
    main()