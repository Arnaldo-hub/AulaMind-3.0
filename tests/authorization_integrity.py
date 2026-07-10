"""Valida autorización real: anónimo 302, teacher 403, admin 200."""
from sqlalchemy import text
from app import app
from database.session import SessionLocal

def run():
    db=SessionLocal(); original=[]
    try:
        rows=db.execute(text(
            "SELECT id, role, is_admin FROM users WHERE is_active = 1 ORDER BY created_at LIMIT 2"
        )).fetchall()
        assert len(rows)>=2, "Se requieren al menos dos usuarios activos."
        teacher_id,admin_id=str(rows[0][0]),str(rows[1][0])
        original=[(str(r[0]),r[1],r[2]) for r in rows]
        db.execute(text("UPDATE users SET role='teacher', is_admin=0 WHERE id=:id"),{"id":teacher_id})
        db.execute(text("UPDATE users SET role='admin', is_admin=1 WHERE id=:id"),{"id":admin_id})
        db.commit()
        client=app.test_client()
        assert client.get("/admin/security-check",follow_redirects=False).status_code==302
        with client.session_transaction() as s: s["user_id"]=teacher_id
        assert client.get("/admin/security-check",follow_redirects=False).status_code==403
        with client.session_transaction() as s: s["user_id"]=admin_id
        assert client.get("/admin/security-check",follow_redirects=False).status_code==200
        print({"anonymous":302,"teacher":403,"admin":200})
        print("AUTHORIZATION INTEGRITY OK")
    finally:
        for uid,role,is_admin in original:
            db.execute(text("UPDATE users SET role=:role, is_admin=:a WHERE id=:id"),
                       {"role":role,"a":is_admin,"id":uid})
        if original: db.commit()
        db.close()

if __name__=="__main__": run()
