
import sys
import termios
import tty
import time
from controladores.instancias import motores, servos_direccion, actuadores_multieje

# Ajustes de pasos para pruebas manuales
PASO_ACTUADOR = 5
PASO_MOTOR = 10 # Porcentaje de velocidad

# Estado inicial simulado (para seguimiento local)
# En un sistema real leeríamos del hardware si fuera posible, o asumiríamos centro.
velocidad_motor = 0
angulo_direccion = 90
angulo_ptz_pan = 90
angulo_ptz_tilt = 90

FLECHA_ARR = '\x1b[A'
FLECHA_ABA = '\x1b[B'
FLECHA_DER = '\x1b[C'
FLECHA_IZQ = '\x1b[D'

def getch():
    """Lee un caracter sin esperar enter (Raw input)"""
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch += sys.stdin.read(2)
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def imprimir_instrucciones():
    print("\n=== TEST DE HARDWARE GENÉRICO ===")
    print("Controles:")
    print("  FLECHA ARRIBA/ABAJO: Motor de Propulsión (0)")
    print("  FLECHA IZQ/DER: Servo de Dirección (0)")
    print("  w/s: PTZ Tilt (Actuador 0)")
    print("  a/d: PTZ Pan (Actuador 0)")
    print("  SPACE: Parada de Emergencia")
    print("  CTRL+C or q: Salir")
    print("=================================\n")

def main():
    global velocidad_motor, angulo_direccion, angulo_ptz_pan, angulo_ptz_tilt
    
    # Inicializar ESCs si es necesario
    for m in motores:
        if hasattr(m, 'inicializar_esc'):
            m.inicializar_esc()

    imprimir_instrucciones()

    try:
        while True:
            tecla = getch()
            
            if tecla == FLECHA_ARR:
                velocidad_motor = min(100, velocidad_motor + PASO_MOTOR)
                if motores: motores[0].establecer_velocidad(velocidad_motor)
                
            elif tecla == FLECHA_ABA:
                velocidad_motor = max(-100, velocidad_motor - PASO_MOTOR)
                if motores: motores[0].establecer_velocidad(velocidad_motor)

            elif tecla == FLECHA_IZQ: # Izquierda = Menos ángulo
                angulo_direccion = max(0, angulo_direccion - PASO_ACTUADOR)
                if servos_direccion: servos_direccion[0].establecer_angulo(angulo_direccion)

            elif tecla == FLECHA_DER: # Derecha = Más ángulo
                angulo_direccion = min(180, angulo_direccion + PASO_ACTUADOR)
                if servos_direccion: servos_direccion[0].establecer_angulo(angulo_direccion)

            # Control PTZ (Asumiendo que es el primer actuador multieje)
            elif tecla == 'w':
                angulo_ptz_tilt = min(180, angulo_ptz_tilt + PASO_ACTUADOR)
                if actuadores_multieje: actuadores_multieje[0].mover_eje('tilt', angulo_ptz_tilt)
            
            elif tecla == 's':
                angulo_ptz_tilt = max(0, angulo_ptz_tilt - PASO_ACTUADOR)
                if actuadores_multieje: actuadores_multieje[0].mover_eje('tilt', angulo_ptz_tilt)

            elif tecla == 'd':
                angulo_ptz_pan = max(0, angulo_ptz_pan - PASO_ACTUADOR) # Invertido visualmente a veces
                if actuadores_multieje: actuadores_multieje[0].mover_eje('pan', angulo_ptz_pan)

            elif tecla == 'a':
                angulo_ptz_pan = min(180, angulo_ptz_pan + PASO_ACTUADOR)
                if actuadores_multieje: actuadores_multieje[0].mover_eje('pan', angulo_ptz_pan)

            elif tecla == ' ':
                velocidad_motor = 0
                for m in motores: m.establecer_velocidad(0)
                print("¡PARADA DE EMERGENCIA!")

            elif tecla == 'q' or tecla == '\x03':
                break
            
            # Feedback visual limpio
            sys.stdout.write(f"\rMotor: {velocidad_motor}% | Dir: {angulo_direccion}° | PTZ: {angulo_ptz_pan}°/{angulo_ptz_tilt}°   ")
            sys.stdout.flush()

    except Exception as e:
        print(f"\nError durante la prueba: {e}")
    finally:
        print("\nDeteniendo todo...")
        for m in motores: m.establecer_velocidad(0)

if __name__ == "__main__":
    main()
