import json
import os

CORRECTIONS = {
    "tecnol": "Tecnología",
    "orient": "Orientación",
    "efi": "Educación Física y Salud",
}

fixed = 0
for root, dirs, files in os.walk("data_curricular"):
    for fname in files:
        if not fname.endswith(".json"):
            continue
        fpath = os.path.join(root, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, dict):
            continue
        asig = data.get("asignatura", "")
        if asig in CORRECTIONS:
            data["asignatura"] = CORRECTIONS[asig]
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print("OK:", fpath)
            fixed += 1

print("=" * 50)
print("CORREGIDOS:", fixed, "archivos")