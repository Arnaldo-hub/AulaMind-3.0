"""Prueba de cierre parcial: 20 recorridos multimodales coherentes."""
from services.curriculum_engine_v4 import CurriculumEngineV4


def run():
    engine = CurriculumEngineV4()
    idx = engine.index()

    selected = []
    quotas = {"regular": 6, "hc": 4, "tp": 4, "parvularia": 3, "epja": 3}

    for mode, quota in quotas.items():
        for course, subjects in idx[mode].items():
            for subject in subjects:
                rec = engine.record(mode, course, subject)
                assert rec is not None
                assert rec["modalidad"] == mode
                assert rec["curso"] == course
                assert rec["asignatura"] == subject
                assert isinstance(rec["unidades"], list)
                assert isinstance(rec["oa_generales"], list)
                selected.append((mode, course, subject, len(rec["unidades"])))
                quota -= 1
                if quota == 0:
                    break
            if quota == 0:
                break
        assert quota == 0, f"No hay suficientes recorridos para modalidad {mode}"

    assert len(selected) == 20
    # Segunda consulta para comprobar uso del índice cacheado.
    engine.modalities()
    stats = engine.statistics()
    assert stats["cache_hits"] >= 1
    assert stats["modalidades"] == 5

    for n, item in enumerate(selected, 1):
        print(f"{n:02d}. {item[0]} | {item[1]} | {item[2]} | unidades={item[3]}")
    print(stats)
    print("CURRICULUM ENGINE 4.0 PATHS OK: 20")


if __name__ == "__main__":
    run()
