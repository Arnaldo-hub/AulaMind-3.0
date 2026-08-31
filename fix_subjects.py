import re

# ==========================================================
# FIX PLANNING.PY
# ==========================================================
with open("routes/planning.py", "r", encoding="utf-8") as f:
    content = f.read()

# Buscar la funcion api_subjects y reemplazarla completamente
old_func = '''@planning.route("/api/curriculum/subjects/<course>", methods=["GET"])
def api_subjects(course):
    """
    Devuelve asignaturas para un curso.
    Aplica correccion de nombres abreviados antes de enviar
    al frontend, garantizando que siempre se muestren los
    nombres oficiales completos.
    """
    subjects = curriculum_service.get_subjects(course)

    # Correccion definitiva: reemplazar abreviaturas
    corrected = [
        _SUBJECT_NAME_MAP.get(s, s)
        for s in subjects
    ]

    return jsonify({
        "success": True,
        "subjects": corrected
    })'''

new_func = '''# ==========================================================
# API ASIGNATURAS — CORRECCION DEFINITIVA
# ==========================================================

_SUBJECT_NAME_MAP = {
    "tecnol": "Tecnología",
    "orient": "Orientación",
    "efi": "Educación Física y Salud",
}


@planning.route("/api/curriculum/subjects/<course>", methods=["GET"])
def api_subjects(course):
    subjects = curriculum_service.get_subjects(course)
    corrected = [_SUBJECT_NAME_MAP.get(s, s) for s in subjects]
    return jsonify({"success": True, "subjects": corrected})'''

if old_func in content:
    content = content.replace(old_func, new_func)
    print("OK: planning.py corregido")
else:
    # Si no encuentra el patron exacto, buscar y reemplazar la funcion
    pattern = r'@planning\.route\("/api/curriculum/subjects/<course>"[^}]*?\n\)\ndef api_subjects\(course\):.*?(?=^@planning\.route|\Z)'
    import re
    match = re.search(pattern, content, re.DOTALL | re.MULTILINE)
    if match:
        content = content[:match.start()] + new_func + '\n\n' + content[match.end():]
        print("OK: planning.py corregido (metodo alternativo)")
    else:
        print("ERROR: No se encontro api_subjects en planning.py")

with open("routes/planning.py", "w", encoding="utf-8") as f:
    f.write(content)

# ==========================================================
# FIX CURRICULUM_API.PY
# ==========================================================
with open("routes/curriculum_api.py", "r", encoding="utf-8") as f:
    content = f.read()

# Agregar mapeo despues de curriculum = CurriculumService()
old_line = "curriculum = CurriculumService()"
new_lines = '''curriculum = CurriculumService()

_SUBJECT_NAME_MAP = {
    "tecnol": "Tecnología",
    "orient": "Orientación",
    "efi": "Educación Física y Salud",
}

def _normalize_subject_names(subjects):
    return [_SUBJECT_NAME_MAP.get(s, s) for s in subjects]'''

if old_line in content and "_SUBJECT_NAME_MAP" not in content:
    content = content.replace(old_line, new_lines)
    # Aplicar normalizacion en el endpoint subjects
    content = content.replace(
        "subjects = curriculum.get_subjects(course)\n\n        return jsonify({",
        "subjects = curriculum.get_subjects(course)\n        subjects = _normalize_subject_names(subjects)\n\n        return jsonify({"
    )
    print("OK: curriculum_api.py corregido")
elif "_SUBJECT_NAME_MAP" in content:
    print("OK: curriculum_api.py ya estaba corregido")
else:
    print("ERROR: No se encontro el patron en curriculum_api.py")

with open("routes/curriculum_api.py", "w", encoding="utf-8") as f:
    f.write(content)

print("\n" + "="*50)
print("CORRECCION DEFINITIVA APLICADA")
print("="*50)
print("Ahora ejecuta:")
print("  git add routes/planning.py routes/curriculum_api.py")
print("  git commit -m 'fix: mapeo definitivo nombres asignaturas'")
print("  git push origin main")