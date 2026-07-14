from pathlib import Path

root = Path(__file__).resolve().parents[1]
app = root / "app.py"
text = app.read_text(encoding="utf-8")

import_line = "from routes.curriculum_api_v4 import curriculum_api_v4\n"
register_line = "app.register_blueprint(curriculum_api_v4)\n"

if import_line not in text:
    marker = "from routes.curriculum_api import curriculum_api\n"
    if marker not in text:
        raise SystemExit("No se encontró el punto de importación esperado en app.py")
    text = text.replace(marker, marker + import_line, 1)

if register_line not in text:
    marker = "app.register_blueprint(curriculum_api)\n"
    if marker not in text:
        raise SystemExit("No se encontró el registro curriculum_api en app.py")
    text = text.replace(marker, marker + register_line, 1)

app.write_text(text, encoding="utf-8", newline="\n")
print("OK: Curriculum API v4 registrada sin reemplazar la API v1.")
