# Resource field specification

Pass `--field name:type[:modifier...]` once per field.

Supported types: `str`, `int`, `float`, `bool`, `datetime`, `date`, `UUID`, `Decimal`, and `EmailStr`.

Supported modifiers:

- `optional`: allow `null` on create and in storage.
- `unique`: add a database uniqueness constraint and map violations to HTTP 409.

Names must be snake_case Python identifiers. Reserved generated names are `id`, `created_at`, and `updated_at`. `EmailStr` is stored as a string but validated at the API boundary; its use adds `email-validator` to project dependencies.

The generator adds UUID identity and UTC creation/update timestamps. Read responses expose these fields, but never expose persistence fields that are not explicitly part of the response template.

