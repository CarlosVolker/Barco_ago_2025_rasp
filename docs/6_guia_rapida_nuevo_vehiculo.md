# Guia Rapida: Alta de un Nuevo Vehiculo

Guia practica para dejar una unidad operativa de forma segura en menos de 30 minutos.

## 1) Preparar entorno

1. Copiar entorno base:

```bash
cp .env.example .env
```

2. Editar `.env` con backend real:

- `URL_BACKEND`
- `URL_SIGNALING`
- `BARCO_TOKEN_VINCULACION`
- `SERVIDOR_STUN`
- `SERVIDOR_TURN_*` (obligatorio en 4G/CGNAT)

3. Instalar dependencias siguiendo `docs/4_instalacion.md`.

## 2) Declarar hardware (fuente de verdad)

Editar `config/componentes.py` y ajustar solo lo necesario:

- `MOTORES_PROPULSION`
- `SERVOS_DIRECCION`
- `ACTUADORES_MULTIEJE`
- `CAMARAS`

Regla: el indice de cada lista define el `indice` que recibira comandos remotos.

## 3) Verificar hardware local

Prueba manual (teclado):

```bash
python test_teclado.py
```

Prueba de carga de instancias:

```bash
python test_hardware_mock.py
```

## 4) Provisionar identidad

Iniciar agente:

```bash
python main.py
```

Flujo esperado:

1. Sin identidad local, se usa `BARCO_TOKEN_VINCULACION`.
2. Backend responde `num_serie` y `token_secreto`.
3. Se guarda identidad cifrada en `config/.barco_identidad_segura`.

## 5) Confirmar conexion de extremo a extremo

- WebSocket conectado a signaling.
- Mensaje `inicio_vehiculo` enviado con `config` (capabilities).
- Oferta WebRTC recibida y respondida (`answer`).
- Comandos llegan por DataChannel o fallback WS.
- Telemetria periodic a `/api/vehiculos/telemetria/`.

## Ownership de archivos durante onboarding

- Identidad/secretos: `config/credenciales.py`, `config/.barco_identidad_segura`
- Definicion fisica: `config/componentes.py`
- Conexion y runtime: `cliente_vehiculo.py`, `src/edge_agent/*`
- Drivers: `controladores/*`

## Do-not-break durante alta de unidad

1. No cambiar nombres `tipo` de comandos en frontend/backend.
2. No editar contratos en `src/edge_agent/contracts/*` para "probar rapido".
3. No borrar archivo de identidad salvo factory reset intencional.
4. No usar limites de servo fuera de rango fisico del mecanismo.
5. No omitir TURN en despliegue 4G de campo.

## Pitfalls frecuentes

- Token de vinculacion expirado o reutilizado.
- URL signaling con slash final incorrecto.
- Config de canales PCA9685 duplicada en dos actuadores.
- Intercambio de ejes `pan`/`tilt` por cableado invertido.
- Falsa sensacion de "todo ok" en LAN y falla total en red celular por no tener TURN.

## Checklist final

- [ ] `.env` real cargado.
- [ ] `config/componentes.py` validado.
- [ ] test local de motores/servos exitoso.
- [ ] provisionamiento exitoso.
- [ ] WebRTC video + control activo.
- [ ] telemetria registrada en backend.
