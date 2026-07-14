"""Curriculum Engine 4.0 — índice multimodal, adaptadores y caché."""
from __future__ import annotations
from services.curriculum_adapters.registry import registry

import json
import threading
from copy import deepcopy
from pathlib import Path


class CurriculumEngineV4:
    MODES = ("regular", "hc", "tp", "parvularia", "epja")

    def __init__(self, data_folder=None):
        root = Path(__file__).resolve().parents[1]
        self.data_folder = Path(data_folder) if data_folder else root / "data_curricular"
        self._lock = threading.RLock()
        self._index = None
        self._stats = {}
        self._cache_hits = 0
        self._cache_misses = 0

    def invalidate(self):
        with self._lock:
            self._index = None

    def index(self):
        with self._lock:
            if self._index is not None:
                self._cache_hits += 1
                return self._index
            self._cache_misses += 1
            self._index = {mode: {} for mode in self.MODES}
            loaded = skipped = 0
            for path in sorted(self.data_folder.rglob("*.json")):
                try:
                    data = json.loads(path.read_text(encoding="utf-8", errors="ignore"))
                except Exception:
                    skipped += 1
                    continue
                if not isinstance(data, dict) or self._is_inventory(path, data):
                    continue
                records = self._adapt(path, data)
                if not records:
                    continue
                loaded += 1
                for record in records:
                    self._insert(record)
            self._stats = self._calculate_stats(loaded, skipped)
            return self._index

    @staticmethod
    def _is_inventory(path, data):
        name = path.name.upper()
        return (
            name.startswith("INVENTARIO_")
            or name.startswith("REPORTE_")
            or "proyecto" in data and "detalle" in data and "unidades" not in data
        )

    def _adapt(self, path, data):
        """
        Toda la adaptación curricular queda delegada al
        Adapter Registry.
        """

        try:

            return registry.adapt(path, data)

        except Exception as ex:

            print("[CurriculumRegistry]", ex,)

            return []

    @staticmethod
    def _unit_records(units):
        result = []
        for i, unit in enumerate(units or [], 1):
            if not isinstance(unit, dict):
                continue
            objectives = unit.get("oa") or unit.get("objetivos") or []
            result.append({
                "id": str(unit.get("id") or unit.get("codigo") or i),
                "nombre": unit.get("nombre") or unit.get("titulo") or f"Unidad {i}",
                "oa": objectives if isinstance(objectives, list) else [],
            })
        return result

    def _adapt_regular(self, d):
        return [self._record("regular", "Educación Regular", d.get("curso"), d.get("asignatura"),
                             self._unit_records(d.get("unidades")), d.get("oa") or [], {})]

    def _adapt_hc(self, d):
        return [self._record("hc", d.get("plan") or "Formación Diferenciada HC", d.get("curso"),
                             d.get("asignatura"), self._unit_records(d.get("unidades")),
                             d.get("oa") or [], {"area": d.get("area"), "tipo": d.get("tipo")})]

    def _adapt_tp(self, d):
        units = []
        for i, module in enumerate(d.get("modulos") or [], 1):
            if not isinstance(module, dict):
                continue
            units.append({
                "id": str(module.get("codigo") or i),
                "nombre": module.get("nombre") or module.get("modulo") or f"Módulo {i}",
                "oa": module.get("oa") or module.get("objetivos") or [],
            })
        return [self._record("tp", d.get("sector") or "TP", d.get("curso"), d.get("especialidad"),
                             units, d.get("oa_perfil_egreso") or [],
                             {"sector": d.get("sector"), "mencion": d.get("mencion")})]

    def _adapt_parvularia(self, d):
        units = []
        for i, nucleus in enumerate(d.get("nucleos") or [], 1):
            if not isinstance(nucleus, dict):
                continue
            units.append({
                "id": str(i),
                "nombre": nucleus.get("nombre") or f"Núcleo {i}",
                "oa": nucleus.get("oa") or [],
                "nota": nucleus.get("nota"),
            })
        return [self._record("parvularia", d.get("nivel_curricular") or "Educación Parvularia",
                             d.get("nivel"), d.get("ambito"), units, [],
                             {"estado_curricular": d.get("estado_curricular")})]

    def _adapt_epja(self, d):
        return [self._record("epja", d.get("tramo") or "EPJA", d.get("nivel"), d.get("asignatura"),
                             self._unit_records(d.get("unidades")), d.get("oa") or [],
                             {"marco": d.get("marco"), "estado_curricular": d.get("estado_curricular")})]

    @staticmethod
    def _record(mode, level, course, subject, units, objectives, metadata):
        if not course or not subject:
            return None
        return {
            "modalidad": mode,
            "nivel": str(level or ""),
            "curso": str(course).strip(),
            "asignatura": str(subject).strip(),
            "unidades": units,
            "oa_generales": objectives if isinstance(objectives, list) else [],
            "metadata": {k: v for k, v in metadata.items() if v not in (None, "")},
        }

    def _insert(self, record):
        """
        Inserta un registro curricular en el índice principal.

        Se omiten registros incompletos (curso o asignatura vacíos)
        para evitar claves inválidas en el índice.
        """

        if not record:
            return

        mode = record.get("modalidad")

        course = str(
            record.get("curso", "")
        ).strip()

        subject = str(
            record.get("asignatura", "")
        ).strip()

        if not mode:
            return

        if not course:
            return

        if not subject:
            return

        bucket = self._index.setdefault(mode, {}).setdefault(course, {})

        current = bucket.get(subject)

        if current is None:
            bucket[subject] = record
            return

        # -----------------------------------------------------
        # Conserva el registro con mayor contenido curricular.
        # -----------------------------------------------------

        current_units = len(
            current.get("unidades", [])
        )

        new_units = len(
            record.get("unidades", [])
        )

        if new_units > current_units:
            bucket[subject] = record

    def _calculate_stats(self, loaded, skipped):
        idx = self._index
        return {
            "documentos_adaptados": loaded,
            "json_omitidos_por_error": skipped,
            "modalidades": len([m for m in idx if idx[m]]),
            "cursos": sum(len(courses) for courses in idx.values()),
            "asignaturas": sum(len(subjects) for courses in idx.values() for subjects in courses.values()),
            "unidades": sum(len(rec["unidades"]) for courses in idx.values() for subjects in courses.values() for rec in subjects.values()),
            "oa": sum(
                len(rec["oa_generales"]) + sum(len(u.get("oa", [])) for u in rec["unidades"])
                for courses in idx.values() for subjects in courses.values() for rec in subjects.values()
            ),
        }

    def modalities(self):
        idx = self.index()
        return [{"id": mode, "nombre": mode.upper(), "cursos": len(idx[mode])} for mode in self.MODES if idx[mode]]

    def courses(self, mode):
        return sorted(self.index().get(mode, {}).keys())

    def subjects(self, mode, course):
        return sorted(self.index().get(mode, {}).get(course, {}).keys())

    def record(self, mode, course, subject):
        value = self.index().get(mode, {}).get(course, {}).get(subject)
        return deepcopy(value) if value else None

    def units(self, mode, course, subject):
        rec = self.record(mode, course, subject)
        return rec["unidades"] if rec else []

    def statistics(self):
        self.index()
        result = dict(self._stats)
        result["cache_hits"] = self._cache_hits
        result["cache_misses"] = self._cache_misses
        return result


curriculum_engine_v4 = CurriculumEngineV4()
