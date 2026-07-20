"""
===========================================================
AulaMind Enterprise 3.0

Curriculum Validator

Modelos

Semana 5A.1
===========================================================
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any


# =========================================================
# Estados de validación
# =========================================================


class ValidationStatus(str, Enum):

    VALID = "VALID"

    INCOMPLETE = "INCOMPLETE"

    STRUCTURAL = "STRUCTURAL"

    DUPLICATE = "DUPLICATE"

    SCHEMA_ERROR = "SCHEMA_ERROR"

    REFERENCE_REQUIRED = "REFERENCE_REQUIRED"


# =========================================================
# Error de validación
# =========================================================


@dataclass(slots=True)
class ValidationMessage:

    code: str

    message: str

    severity: str = "ERROR"


# =========================================================
# Resultado por documento
# =========================================================


@dataclass(slots=True)
class ValidationResult:

    path: str

    modalidad: str = ""

    curso: str = ""

    asignatura: str = ""

    estado: ValidationStatus = ValidationStatus.VALID

    errores: List[ValidationMessage] = field(
        default_factory=list
    )

    advertencias: List[ValidationMessage] = field(
        default_factory=list
    )

    metadata: Dict[str, Any] = field(
        default_factory=dict
    )

    # -----------------------------------------------------

    @property
    def valid(self) -> bool:

        return self.estado == ValidationStatus.VALID

    # -----------------------------------------------------

    def add_error(
        self,
        code: str,
        message: str,
    ):

        self.errores.append(

            ValidationMessage(

                code=code,

                message=message,

                severity="ERROR",

            )

        )

    # -----------------------------------------------------

    def add_warning(
        self,
        code: str,
        message: str,
    ):

        self.advertencias.append(

            ValidationMessage(

                code=code,

                message=message,

                severity="WARNING",

            )

        )

    # -----------------------------------------------------

    def set_status(
        self,
        status: ValidationStatus,
    ):

        self.estado = status

    # -----------------------------------------------------

    def to_dict(self):

        return {

            "path":
                self.path,

            "modalidad":
                self.modalidad,

            "curso":
                self.curso,

            "asignatura":
                self.asignatura,

            "estado":
                self.estado.value,

            "errores": [

                {

                    "code": e.code,

                    "message": e.message,

                    "severity": e.severity,

                }

                for e in self.errores

            ],

            "advertencias": [

                {

                    "code": w.code,

                    "message": w.message,

                    "severity": w.severity,

                }

                for w in self.advertencias

            ],

            "metadata":
                self.metadata,

        }


# =========================================================
# Resumen global
# =========================================================


@dataclass(slots=True)
class ValidationSummary:

    total: int = 0

    valid: int = 0

    incomplete: int = 0

    structural: int = 0

    duplicate: int = 0

    schema_error: int = 0

    reference_required: int = 0

    results: List[ValidationResult] = field(
        default_factory=list
    )

    # -----------------------------------------------------

    def add(
        self,
        result: ValidationResult,
    ):

        self.total += 1

        self.results.append(result)

        match result.estado:

            case ValidationStatus.VALID:

                self.valid += 1

            case ValidationStatus.INCOMPLETE:

                self.incomplete += 1

            case ValidationStatus.STRUCTURAL:

                self.structural += 1

            case ValidationStatus.DUPLICATE:

                self.duplicate += 1

            case ValidationStatus.SCHEMA_ERROR:

                self.schema_error += 1

            case ValidationStatus.REFERENCE_REQUIRED:

                self.reference_required += 1

    # -----------------------------------------------------

    @property
    def coverage(self):

        if self.total == 0:

            return 0.0

        return round(

            (self.valid / self.total) * 100,

            2,

        )

    # -----------------------------------------------------

    def to_dict(self):

        return {

            "total":
                self.total,

            "valid":
                self.valid,

            "incomplete":
                self.incomplete,

            "structural":
                self.structural,

            "duplicate":
                self.duplicate,

            "schema_error":
                self.schema_error,

            "reference_required":
                self.reference_required,

            "coverage":
                self.coverage,

        }