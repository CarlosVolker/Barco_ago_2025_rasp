# Contexto Hardware y Control

## Fuente de verdad de hardware

- `config/componentes.py` define motores, servos, actuadores y camaras.
- El orden de listas define indices de comandos remotos.

## Construccion de instancias

- `controladores/instancias.py` crea:
  - `motores`
  - `servos_direccion`
  - `actuadores_multieje`

## Ejecucion de comandos

- `src/edge_agent/control/runtime.py` aplica comandos validados a instancias.
- Validacion previa viene desde `legacy_adapter.validate_control_command`.

## Ownership por ruta

- Config fisica: `config/componentes.py`
- Driver motor ESC: `controladores/motor_brushless.py`
- Driver servo: `controladores/actuador_servo.py`
- Driver multieje: `controladores/actuador_ejes.py`
- Driver PCA9685: `controladores/pca9685_manager.py`

## Do-not-break hardware

1. No invertir polaridad logica de velocidad sin migracion coordinada.
2. No romper neutral `0` para ESC.
3. No cambiar nombres de ejes (`pan`, `tilt`, etc.) sin actualizar configuracion y frontend.
4. No exceder limites de angulo establecidos.

## Pitfalls de campo

- Limites de angulo muy amplios causando bloqueo mecanico.
- Canales PCA9685 duplicados en actuadores diferentes.
- Probar motores sin alimentar ESC/servos adecuadamente.
