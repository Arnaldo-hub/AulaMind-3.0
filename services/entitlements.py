"""
===========================================================
AulaMind Enterprise 3.0
services/entitlements.py
-----------------------------------------------------------

EL PORTERO COMERCIAL de AulaMind (v3.1).

Un solo punto decide si un usuario puede generar con IA:

- Admin            → siempre permitido
- Plan pagado      → permitido (tope mensual del plan)
- Trial 3 días     → permitido (tope de generaciones)
- Vencido / sin cupo → bloqueado con razón para el paywall

También gestiona:

- Creación del trial al registrarse
- Expiración automática (evaluación perezosa al usar)
- Correos día 0 / día 2 / día 3 (vía TrialMailer)
- Activación manual de planes (admin) y futura por
  webhook de Mercado Pago (v3.2)

Autor:
Biotecno Chile
===========================================================
"""

import logging
from datetime import datetime
from datetime import timedelta

from flask import current_app

from database.session import SessionLocal
from models.ai_generation import AIGeneration
from models.subscription import Subscription
from models.user import User
from models.user_subscription import UserSubscription
from services.trial_mailer import TrialMailer

logger = logging.getLogger(__name__)


class Entitlements:

    # =====================================================
    # Planes por defecto (idempotente)
    # =====================================================

    @staticmethod
    def ensure_default_plans(db):

        config = current_app.config

        trial_name = config.get("TRIAL_PLAN_NAME", "Trial")
        pro_name = config.get("PRO_PLAN_NAME", "Pro")
        pro_price = config.get("PRO_MONTHLY_PRICE_CLP", 9990)

        plans = {
            row.name: row
            for row in db.query(Subscription).all()
        }

        if trial_name not in plans:

            db.add(Subscription(
                name=trial_name,
                description=(
                    "Prueba gratuita: días y generaciones "
                    "limitadas según configuración."
                ),
                monthly_price=0.0,
                yearly_price=0.0,
                monthly_ai_requests=config.get(
                    "TRIAL_MAX_GENERATIONS", 10
                ),
                max_documents=20,
                max_storage_mb=100,
                max_exports_per_month=10,
                active=True,
            ))

        if pro_name not in plans:

            db.add(Subscription(
                name=pro_name,
                description=(
                    "Plan individual: generación amplia de "
                    "documentos pedagógicos con IA."
                ),
                monthly_price=float(pro_price),
                yearly_price=float(pro_price * 10),
                monthly_ai_requests=1000,
                max_documents=1000,
                max_storage_mb=2000,
                max_exports_per_month=500,
                active=True,
            ))

        db.flush()

        return {
            row.name: row
            for row in db.query(Subscription).all()
        }

    # =====================================================
    # Crear trial (al registrarse)
    # =====================================================

    @staticmethod
    def create_trial(db, user):

        config = current_app.config
        plans = Entitlements.ensure_default_plans(db)
        trial_plan = plans[config.get("TRIAL_PLAN_NAME", "Trial")]

        now = datetime.utcnow()
        days = config.get("TRIAL_DAYS", 3)

        sub = UserSubscription(
            user_id=user.id,
            subscription_id=trial_plan.id,
            status="trial",
            starts_at=now,
            ends_at=now + timedelta(days=days),
            generations_used=0,
            source="auto_trial",
        )

        db.add(sub)
        db.commit()
        db.refresh(sub)

        TrialMailer.send_welcome(
            user.email,
            user.first_name or "docente",
            days,
            config.get("TRIAL_MAX_GENERATIONS", 10),
        )

        return sub

    # =====================================================
    # Activar plan pagado (admin manual / webhook v3.2)
    # =====================================================

    @staticmethod
    def activate_paid(db, user_id, days=30, source="manual"):

        config = current_app.config
        plans = Entitlements.ensure_default_plans(db)
        pro_plan = plans[config.get("PRO_PLAN_NAME", "Pro")]

        sub = db.query(UserSubscription).filter(
            UserSubscription.user_id == str(user_id)
        ).first()

        now = datetime.utcnow()

        if sub is None:

            sub = UserSubscription(
                user_id=str(user_id),
                subscription_id=pro_plan.id,
            )
            db.add(sub)

        sub.subscription_id = pro_plan.id
        sub.status = "active"
        sub.starts_at = now
        sub.ends_at = now + timedelta(days=days)
        sub.generations_used = 0
        sub.source = source
        sub.warning_sent_at = None
        sub.expired_sent_at = None

        db.commit()
        db.refresh(sub)

        return sub

    # =====================================================
    # EL PORTERO: ¿puede generar?
    # =====================================================

    @staticmethod
    def check_generation(user_id):

        config = current_app.config
        db = SessionLocal()

        try:

            user = db.query(User).filter(
                User.id == str(user_id)
            ).first()

            if user is None:
                return {
                    "allowed": False,
                    "reason": "no_user",
                    "message": "Usuario no encontrado.",
                }

            # Admin siempre pasa (dueño de la plataforma)
            if user.role == "admin":
                return {
                    "allowed": True,
                    "reason": "admin",
                    "status": "admin",
                    "plan_name": "Admin",
                }

            plans = Entitlements.ensure_default_plans(db)

            sub = db.query(UserSubscription).filter(
                UserSubscription.user_id == user.id
            ).first()

            # Usuario antiguo sin suscripción → trial perezoso
            if sub is None:
                sub = Entitlements._create_trial_silent(
                    db, user, plans, config
                )

            now = datetime.utcnow()

            # ----------------------------------------------
            # Plan pagado activo
            # ----------------------------------------------

            if sub.status == "active":

                if sub.ends_at and now > sub.ends_at:
                    return Entitlements._expire(
                        db, user, sub, "subscription_expired",
                        "Tu suscripción venció. Renuévala para "
                        "seguir generando."
                    )

                monthly_cap = sub.plan.monthly_ai_requests

                used_month = db.query(AIGeneration).filter(
                    AIGeneration.user_id == user.id,
                    AIGeneration.success == True,  # noqa: E712
                    AIGeneration.created_at >= now.replace(
                        day=1, hour=0, minute=0,
                        second=0, microsecond=0
                    ),
                ).count()

                if monthly_cap and used_month >= monthly_cap:
                    return {
                        "allowed": False,
                        "reason": "monthly_quota",
                        "status": sub.status,
                        "plan_name": sub.plan.name,
                        "message": (
                            "Alcanzaste el tope mensual de tu plan. "
                            "Contáctanos para ampliarlo."
                        ),
                    }

                return {
                    "allowed": True,
                    "reason": "paid",
                    "status": sub.status,
                    "plan_name": sub.plan.name,
                    "ends_at": sub.ends_at,
                }

            # ----------------------------------------------
            # Trial
            # ----------------------------------------------

            max_gen = config.get("TRIAL_MAX_GENERATIONS", 10)

            if sub.ends_at and now > sub.ends_at:
                return Entitlements._expire(
                    db, user, sub, "trial_expired",
                    "Tu trial de "
                    f"{config.get('TRIAL_DAYS', 3)} días terminó. "
                    "Suscríbete para seguir generando."
                )

            if sub.generations_used >= max_gen:
                return {
                    "allowed": False,
                    "reason": "trial_quota",
                    "status": sub.status,
                    "plan_name": sub.plan.name,
                    "message": (
                        f"Usaste tus {max_gen} generaciones de "
                        "prueba. Suscríbete para seguir generando."
                    ),
                    "remaining_generations": 0,
                    "ends_at": sub.ends_at,
                }

            # Aviso "queda 1 día" (una sola vez)
            hours_left = (sub.ends_at - now).total_seconds() / 3600

            if hours_left <= 24 and sub.warning_sent_at is None:

                if TrialMailer.send_warning(
                    user.email,
                    user.first_name or "docente",
                    max_gen - sub.generations_used,
                ):
                    sub.warning_sent_at = now
                    db.commit()

            return {
                "allowed": True,
                "reason": "trial",
                "status": sub.status,
                "plan_name": sub.plan.name,
                "remaining_generations": max_gen - sub.generations_used,
                "ends_at": sub.ends_at,
            }

            # ----------------------------------------------
            # expired / cancelled → bloqueado
            # ----------------------------------------------

            return {
                "allowed": False,
                "reason": "subscription_inactive",
                "status": sub.status,
                "plan_name": sub.plan.name if sub.plan else "",
                "message": (
                    "Tu suscripción no está activa. "
                    "Suscríbete para seguir generando."
                ),
            }

        finally:
            db.close()

    # =====================================================
    # Registrar una generación consumida
    # =====================================================

    @staticmethod
    def record_generation(user_id):

        db = SessionLocal()

        try:

            sub = db.query(UserSubscription).filter(
                UserSubscription.user_id == str(user_id)
            ).first()

            if sub is not None and sub.status == "trial":
                sub.generations_used = (sub.generations_used or 0) + 1
                db.commit()

        except Exception:
            db.rollback()
            logger.exception(
                "No se pudo registrar generación de %s", user_id
            )

        finally:
            db.close()

    # =====================================================
    # Estado para la página "Mi Plan"
    # =====================================================

    @staticmethod
    def get_status(user_id):

        result = Entitlements.check_generation(user_id)

        config = current_app.config

        result["trial_days"] = config.get("TRIAL_DAYS", 3)
        result["trial_max"] = config.get("TRIAL_MAX_GENERATIONS", 10)
        result["pro_price"] = config.get("PRO_MONTHLY_PRICE_CLP", 9990)

        return result

    # =====================================================
    # Helpers internos
    # =====================================================

    @staticmethod
    def _create_trial_silent(db, user, plans, config):

        trial_plan = plans[config.get("TRIAL_PLAN_NAME", "Trial")]
        now = datetime.utcnow()

        sub = UserSubscription(
            user_id=user.id,
            subscription_id=trial_plan.id,
            status="trial",
            starts_at=now,
            ends_at=now + timedelta(
                days=config.get("TRIAL_DAYS", 3)
            ),
            generations_used=0,
            source="auto_trial",
        )

        db.add(sub)
        db.commit()
        db.refresh(sub)

        return sub

    @staticmethod
    def _expire(db, user, sub, reason, message):

        sub.status = "expired"

        if sub.expired_sent_at is None:

            if TrialMailer.send_expired(
                user.email,
                user.first_name or "docente",
            ):
                sub.expired_sent_at = datetime.utcnow()

        db.commit()

        return {
            "allowed": False,
            "reason": reason,
            "status": "expired",
            "plan_name": sub.plan.name if sub.plan else "",
            "message": message,
        }
