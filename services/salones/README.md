# Microservicio de salones (ms-salones)

Primer servicio extraído del monolito SGS. Expone `/api/salones` y se alcanza a través del API Gateway.

## Principios SOLID

- **S** — `app.py` solo HTTP, `SalonService` solo negocio, los repositorios solo persistencia.
- **O** — se puede agregar `MySQLSalonRepository` sin modificar `SalonService`.
- **L** — `PostgresSalonRepository` y `MemorySalonRepository` sustituyen a `ISalonRepository`.
- **I** — `ISalonRepository` solo declara `listar`, `crear` y `actualizar`.
- **D** — `SalonService` depende de la abstracción, no de Postgres. La implementación se inyecta en `create_app()`.
