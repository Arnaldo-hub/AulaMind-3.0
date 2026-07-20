from services.curriculum_engine_v4 import curriculum_engine_v4
from services.planning.dua import dua_engine


def main():

    record = curriculum_engine_v4.record(
        "regular",
        "1° básico",
        "Artes Visuales",
    )

    assert record is not None

    dua = dua_engine.generate(record)

    assert dua is not None

    assert "principio1" in dua
    assert "principio2" in dua
    assert "principio3" in dua
    assert "adecuaciones" in dua
    assert "apoyos" in dua

    print("=" * 60)
    print("DUA Engine OK")
    print("=" * 60)

    print()

    print("Principio I")

    for item in dua["principio1"]:
        print(" •", item)

    print()

    print("Adecuaciones")

    for item in dua["adecuaciones"]:
        print(
            f" • [{item['tipo']}] {item['descripcion']}"
        )


if __name__ == "__main__":
    main()