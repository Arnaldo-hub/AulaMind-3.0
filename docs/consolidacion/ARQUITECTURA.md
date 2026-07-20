# Arquitectura Oficial

```
Frontend
        │
        ▼
FastAPI
        │
        ▼
Routers
        │
        ▼
Providers
        │
        ▼
Services
        │
        ▼
Domain Engines
        │
        ▼
Curriculum
```

---

## Responsabilidades

### Routers

Exponen la API REST.

Nunca contienen lógica de negocio.

---

### Providers

Preparan la información para la API.

---

### Services

Implementan reglas de negocio.

---

### Engines

Implementan el dominio curricular.

---

### Data

Información curricular oficial.

---

Esta arquitectura constituye el estándar oficial de AulaMind Enterprise 3.0.

## Núcleo Curricular

El dominio curricular se implementa mediante CurriculumRepository.

```
CurriculumRepository

├── Loader

├── Index

├── Search

└── Curriculum Data
```

Todos los módulos deberán acceder al currículo exclusivamente mediante este componente.