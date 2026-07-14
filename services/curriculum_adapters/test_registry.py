import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from services.curriculum_adapters.registry import registry


def test_registry():

    print("Adaptadores registrados:")

    stats = registry.statistics()

    print(stats)

    assert stats["registered_adapters"] == 5

    print("Registry OK")


if __name__ == "__main__":

    test_registry()