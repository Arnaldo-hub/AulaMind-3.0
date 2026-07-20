"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Auditor

Ranking Engine

Semana 6.4
===========================================================
"""

from __future__ import annotations


class RankingEngine:
    """
    Genera rankings ejecutivos utilizando los
    resultados producidos por StatisticsEngine.
    """

    VERSION = "6.4"

    # ---------------------------------------------------------

    def build(
        self,
        statistics: dict,
    ) -> dict:

        top_valid = list(
            statistics.get(
                "top_valid",
                [],
            )
        )

        top_incomplete = list(
            statistics.get(
                "top_incomplete",
                [],
            )
        )

        duplicates = list(
            statistics.get(
                "duplicates",
                [],
            )
        )

        modalities = statistics.get(
            "modalities",
            {},
        )

        courses = statistics.get(
            "courses",
            {},
        )

        subjects = statistics.get(
            "subjects",
            {},
        )

        return {

            "top_valid": top_valid,

            "top_incomplete": top_incomplete,

            "duplicates": duplicates,

            "modalities": self._sort_counter(
                modalities
            ),

            "courses": self._sort_counter(
                courses
            ),

            "subjects": self._sort_counter(
                subjects
            ),

        }

    # ---------------------------------------------------------

    @staticmethod
    def _sort_counter(counter):

        return sorted(

            counter.items(),

            key=lambda item: (

                -item[1],

                item[0],

            ),

        )

    # ---------------------------------------------------------

    def statistics(self):

        return {

            "module": "Ranking Engine",

            "version": self.VERSION,

            "outputs": [

                "top_valid",

                "top_incomplete",

                "duplicates",

                "modalities",

                "courses",

                "subjects",

            ],

        }


ranking_engine = RankingEngine()