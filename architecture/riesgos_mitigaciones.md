# Riesgos y Mitigaciones
- **Fallo en API pública:** Si la API externa no responde, el pipeline aplica reintentos automáticos con tiempos de espera incrementales.
- **Cambios de esquema:** Validaciones mediante contratos de datos JSON en data_contract/schema/.
- **Idempotencia:** La capa Gold usa WRITE_TRUNCATE para evitar registros duplicados en re-ejecuciones.