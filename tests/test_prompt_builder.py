from services.curriculum_engine_v4 import curriculum_engine_v4

from services.planning.didactics import didactic_engine
from services.planning.evaluations import evaluation_engine
from services.planning.resources import resources_engine
from services.planning.dua import dua_engine
from services.planning.indicators import indicators_engine
from services.planning.prompt_builder import prompt_builder


def main():

    curriculum = curriculum_engine_v4.record(
        "regular",
        "1° básico",
        "Artes Visuales",
    )

    assert curriculum is not None

    prompt = prompt_builder.build(

        curriculum,

        didactic_engine.generate(curriculum),

        evaluation_engine.generate(curriculum),

        resources_engine.generate(curriculum),

        dua_engine.generate(curriculum),

        indicators_engine.generate(curriculum),

    )

    assert isinstance(prompt, str)

    assert len(prompt) > 200

    print("=" * 60)
    print("Prompt Builder OK")
    print("=" * 60)
    print()
    print(prompt[:700])
    print("...")
    print()
    print(f"Longitud del prompt: {len(prompt)} caracteres")


if __name__ == "__main__":
    main()