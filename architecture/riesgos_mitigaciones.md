# Riesgos y Mitigaciones
- **Fallo en API pública:** Si la API externa no responde, el pipeline aplica reintentos automáticos y preserva la data cruda disponible.
- **Cambios de esquema:** Validaciones mediante contratos de datos JSON en data_contract/schema/.
- **Idempotencia:** La capa Gold usa WRITE_TRUNCATE / particiones para evitar duplicidad de registros en re-ejecuciones.