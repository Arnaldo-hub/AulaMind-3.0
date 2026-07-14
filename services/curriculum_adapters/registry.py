"""
===========================================================
AulaMind Enterprise 3.0
Curriculum Engine 4.0

Registry de Adaptadores Curriculares
===========================================================
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .base import CurriculumAdapter


class AdapterRegistry:
    """
    Registro central de adaptadores curriculares.
    """

    def __init__(self):

        self._adapters: list[CurriculumAdapter] = []

    # --------------------------------------------------

    def register(
        self,
        adapter: CurriculumAdapter,
    ) -> None:

        self._adapters.append(adapter)

        self._adapters.sort(
            key=lambda a: a.priority,
            reverse=True,
        )

    # --------------------------------------------------

    def adapters(
        self,
    ) -> list[CurriculumAdapter]:

        return self._adapters

    # --------------------------------------------------

    def get_adapter(
        self,
        path: Path,
        data: dict[str, Any],
    ) -> CurriculumAdapter | None:

        for adapter in self._adapters:

            try:

                if adapter.can_handle(path, data):

                    return adapter

            except Exception:

                continue

        return None

    # --------------------------------------------------

    def adapt(
        self,
        path: Path,
        data: dict[str, Any],
    ) -> list[dict]:

        adapter = self.get_adapter(path, data)

        if adapter is None:

            return []

        return adapter.adapt(path, data)

    # --------------------------------------------------

    def statistics(self) -> dict:

        return {

            "registered_adapters": len(
                self._adapters
            ),

            "modalidades": [

                adapter.mode

                for adapter in self._adapters

            ],

        }


# ==========================================================
# Registro global
# ==========================================================

registry = AdapterRegistry()


# ==========================================================
# Registro de adaptadores
# ==========================================================

def load_default_adapters():

    from .regular import RegularAdapter
    from .hc import HCAdapter
    from .tp import TPAdapter
    from .parvularia import ParvulariaAdapter
    from .epja import EPJAAdapter

    registry.register(
        RegularAdapter()
    )

    registry.register(
        HCAdapter()
    )

    registry.register(
        TPAdapter()
    )

    registry.register(
        ParvulariaAdapter()
    )

    registry.register(
        EPJAAdapter()
    )


load_default_adapters()