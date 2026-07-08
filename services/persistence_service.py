from sqlalchemy import func, select
from database.session import SessionLocal
from models.document import Document
from models.ai_generation import AIGeneration
from models.usage_event import UsageEvent

class PersistenceService:
    @staticmethod
    def save_generated_document(user_id, school_id, document_type, payload, result):
        db = SessionLocal()
        try:
            content = result.get("content", "")
            title = f"{document_type.title()} - {payload.get('asignatura','')} - {payload.get('curso','')}".strip(" -")
            doc = Document(
                user_id=str(user_id),
                school_id=school_id,
                document_type=document_type,
                title=title or document_type.title(),
                course=payload.get("curso"),
                subject=payload.get("asignatura"),
                unit=payload.get("unidad"),
                topic=payload.get("tema"),
                objectives_json=payload.get("objetivos") or payload.get("objetivo"),
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
                metadata_json={"document_id": doc.id},
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
                select(Document.document_type, func.count(Document.id))
                .where(Document.user_id == str(user_id))
                .group_by(Document.document_type)
            ).all()
            counts = dict(rows)
            total = sum(counts.values())
            return {
                "planning_count": counts.get("planning", 0),
                "evaluation_count": counts.get("evaluation", 0),
                "guide_count": counts.get("guide", 0),
                "rubric_count": counts.get("rubric", 0),
                "total_documents": total,
                "time_saved_hours": round(total * 1.5, 1),
            }
        finally:
            db.close()

persistence_service = PersistenceService()
