from services.curriculum_engine_v4 import curriculum_engine_v4
from services.planning.resources import resources_engine


def main():

    record = curriculum_engine_v4.record(
        "regular",
        "1° básico",
        "Artes Visuales",
    )

    assert record is not None

    resources = resources_engine.generate(
        record
    )

    assert resources is not None

    assert "material_concreto" in resources
    assert "recursos_digitales" in resources
    assert "tic" in resources
    assert "bibliografia" in resources

    print("=" * 60)
    print("Resources Engine OK")
    print("=" * 60)

    print()

    print("Material Concreto")

    for item in resources["material_concreto"]:
        print(" •", item)

    print()

    print("Recursos Digitales")

    for item in resources["recursos_digitales"]:
        print(" •", item["nombre"])


if __name__ == "__main__":
    main()