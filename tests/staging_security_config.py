"""Valida configuración de seguridad sin conexiones externas."""
from app import app

def run():
    c=app.config
    storage=c.get("RATELIMIT_STORAGE_URI","")
    assert storage, "RATELIMIT_STORAGE_URI vacío"
    if not c.get("DEBUG"):
        assert storage!="memory://", "Staging/producción no puede usar memory://"
        assert c.get("SECRET_KEY")!="AulaMind-Local-Development-Only"
        assert c.get("SESSION_COOKIE_SECURE") is True
    if c.get("MAIL_SERVER"):
        assert c.get("MAIL_FROM"), "MAIL_FROM requerido con SMTP"
        assert not (c.get("MAIL_USE_TLS") and c.get("MAIL_USE_SSL"))
    print({"debug":bool(c.get("DEBUG")),"rate_limit_storage":"configured",
           "smtp":"configured" if c.get("MAIL_SERVER") else "dev_mode",
           "secure_cookie":bool(c.get("SESSION_COOKIE_SECURE"))})
    print("STAGING SECURITY CONFIG OK")

if __name__=="__main__": run()
