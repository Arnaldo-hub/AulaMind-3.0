"""
===========================================================
AulaMind Enterprise 3.0
routes/jobs.py
-----------------------------------------------------------
Polling de estado de jobs encolados en RQ
===========================================================
"""

from flask import Blueprint, jsonify, session
from rq.job import Job
from services.queue_service import get_redis_url
from redis import Redis

jobs = Blueprint("jobs", __name__, url_prefix="/jobs")


@jobs.route("/<job_id>/status")
def job_status(job_id):
    if "user_id" not in session:
        return jsonify(success=False, error="No autenticado"), 401

    redis_conn = Redis.from_url(get_redis_url())
    try:
        job = Job.fetch(job_id, connection=redis_conn)
    except Exception:
        return jsonify(success=False, error="Job no encontrado"), 404

    response = {
        "success": True,
        "job_id": job_id,
        "status": job.get_status(),  # queued / started / finished / failed
        "enqueued_at": job.enqueued_at.isoformat() if job.enqueued_at else None,
        "started_at": job.started_at.isoformat() if job.started_at else None,
        "ended_at": job.ended_at.isoformat() if job.ended_at else None,
    }

    if job.is_finished:
        result = job.return_value or {}
        response["result"] = result
        if result.get("success") and result.get("document_id"):
            response["document_id"] = result["document_id"]

    elif job.is_failed:
        response["error"] = str(job.exc_info) if job.exc_info else "Error desconocido en worker"

    return jsonify(response)