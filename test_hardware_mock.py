import sys
import os

# Agregamos el directorio actual al path para que los imports funcionen
sys.path.append(os.getcwd())

print("--- INICIANDO TEST DE HARDWARE (MOCK) ---")

try:
    from controladores.instancias import motores, servos_direccion, actuadores_multieje
    from controladores.pca9685_manager import GestorPCA9685
    
    print("\n[OK] Módulos importados correctamente.")
    
    # Verificar que las instancias se crearon
    print(f"Motores encontrados: {len(motores)}")
    for m in motores:
        print(f" - Motor: {m.nombre} en Canal PCA {m.canal} Dir 0x{m.direccion_i2c:X}")
        # Prueba de movimiento
        m.establecer_velocidad(50)
        
    print(f"\nServos encontrados: {len(servos_direccion)}")
    for s in servos_direccion:
        print(f" - Servo: {s.nombre} en Canal PCA {s.canal}")
        s.establecer_angulo(90)
        
    print(f"\nActuadores Multi-Eje encontrados: {len(actuadores_multieje)}")
    for a in actuadores_multieje:
        print(f" - Actuador: {a.nombre}")
        for eje in a.canales:
            a.mover_eje(eje, 45)

    print("\n--- TEST FINALIZADO CON ÉXITO ---")
    print("El sistema está listo para soportar múltiples placas PCA9685.")

except Exception as e:
    print(f"\n[ERROR CRÍTICO] Falta en verificación: {e}")
    import traceback
    traceback.print_exc()
