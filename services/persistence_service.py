from sqlalchemy import func, select
from database.session import SessionLocal
from models.document import Document
from models.ai_generation import AIGeneration
from models.usage_event import UsageEvent
from models.export import Export


class PersistenceService:

    @staticmethod
    def save_generated_document(
        user_id,
        school_id,
        document_type,
        payload,
        result
    ):
        db = SessionLocal()

        try:

            content = result.get("content", "")

            title = (
                f"{document_type.title()} - "
                f"{payload.get('asignatura','')} - "
                f"{payload.get('curso','')}"
            ).strip(" -")

            doc = Document(
                user_id=str(user_id),
                school_id=school_id,
                document_type=document_type,
                title=title or document_type.title(),
                course=payload.get("curso"),
                subject=payload.get("asignatura"),
                unit=payload.get("unidad"),
                topic=payload.get("tema"),
                objectives_json=payload.get("objetivos")
                or payload.get("objetivo"),
                input_json=payload,
                content=content,
            )
            db.add(doc)
            db.flush()

            generation = AIGeneration(
                user_id=str(user_id),
                document_id=doc.id,
                feature=document_type,
                success=True,
            )

            event = UsageEvent(
                user_id=str(user_id),
                school_id=school_id,
                event_type="ai_generation",
                feature=document_type,
                quantity=1,
                metadata_json={
                    "document_id": doc.id
                },
            )

            db.add_all([generation, event])

            db.commit()

            return doc.id

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()

    @staticmethod
    def dashboard_stats(user_id):

        db = SessionLocal()

        try:

            rows = db.execute(
                select(
                    Document.document_type,
                    func.count(Document.id)
                )
                .where(
                    Document.user_id == str(user_id)
                )
                .group_by(
                    Document.document_type
                )
            ).all()

            counts = dict(rows)

            total = sum(counts.values())

            export_count = db.scalar(
                select(func.count(Export.id))
                .where(
                    Export.user_id == str(user_id)
                )
            ) or 0

            return {
                "planning_count": counts.get("planning", 0),
                "evaluation_count": counts.get("evaluation", 0),
                "guide_count": counts.get("guide", 0),
                "rubric_count": counts.get("rubric", 0),
                "export_count": export_count,
                "total_documents": total,
                "time_saved_hours": round(total * 1.5, 1),
            }

        finally:

            db.close()
    # ==========================================================
    # LISTAR DOCUMENTOS
    # ==========================================================

    @staticmethod
    def list_documents(user_id, document_type=None):

        db = SessionLocal()

        try:

            query = select(Document).where(
                Document.user_id == str(user_id)
            )

            if document_type:

                query = query.where(
                    Document.document_type == document_type
                )

            query = query.order_by(
                Document.created_at.desc()
            )

            rows = db.execute(query).scalars().all()

            resultado = []

            for doc in rows:

                resultado.append({
                    "id": doc.id,
                    "title": doc.title,
                    "document_type": doc.document_type,
                    "course": doc.course,
                    "subject": doc.subject,
                    "unit": doc.unit,
                    "created_at": (
                        doc.created_at.isoformat()
                        if doc.created_at else None
                    )
                })

            return resultado

        finally:

            db.close()
    # ==========================================================
    # OBTENER DOCUMENTO
    # ==========================================================

    @staticmethod
    def get_document(document_id, user_id):

        db = SessionLocal()

        try:

            query = select(Document).where(
                Document.id == document_id,
                Document.user_id == str(user_id)
            )

            return db.execute(query).scalar_one_or_none()

        finally:

            db.close()


    # ==========================================================
    # ELIMINAR DOCUMENTO
    # ==========================================================

    @staticmethod
    def delete_document(document_id, user_id):

        db = SessionLocal()

        try:

            document = db.execute(
                select(Document).where(
                    Document.id == document_id,
                    Document.user_id == str(user_id)
                )
            ).scalar_one_or_none()

            if document:

                db.delete(document)

                db.commit()

                return True

            return False

        except Exception:

            db.rollback()

            raise

        finally:

            db.close()


# ==========================================================
# INSTANCIA DEL SERVICIO
# ESTA DEBE SER LA ÚLTIMA LÍNEA DEL ARCHIVO
# ==========================================================

persistence_service = PersistenceService()
