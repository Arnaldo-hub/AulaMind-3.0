"""Auditoría de integridad del núcleo SaaS, sin llamar a OpenAI."""
from sqlalchemy import func, select
from database.session import SessionLocal
from models.document import Document
from models.ai_generation import AIGeneration
from models.export import Export
from models.usage_event import UsageEvent

db = SessionLocal()
try:
    docs = db.scalar(select(func.count()).select_from(Document)) or 0
    gens = db.scalar(select(func.count()).select_from(AIGeneration)) or 0
    events = db.scalar(select(func.count()).select_from(UsageEvent)) or 0
    exports = db.scalar(select(func.count()).select_from(Export)) or 0
    orphan_gens = db.scalar(select(func.count()).select_from(AIGeneration).outerjoin(Document, AIGeneration.document_id == Document.id).where(AIGeneration.document_id.is_not(None), Document.id.is_(None))) or 0
    orphan_exports = db.scalar(select(func.count()).select_from(Export).outerjoin(Document, Export.document_id == Document.id).where(Document.id.is_(None))) or 0
    print({"documents": docs, "ai_generations": gens, "usage_events": events, "exports": exports, "orphan_ai_generations": orphan_gens, "orphan_exports": orphan_exports})
    assert orphan_gens == 0
    assert orphan_exports == 0
    assert gens >= docs, "Cada documento generado debe tener trazabilidad IA."
    assert events >= docs, "Cada documento generado debe tener evento de consumo."
    print("PERSISTENCE INTEGRITY OK")
finally:
    db.close()
