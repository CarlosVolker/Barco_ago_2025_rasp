
import sys
import termios
import tty
import os
import time
from controladores.instancias import motores_brushless, timones, torretas

INCREMENTO_TORRETA = 5
INCREMENTO_TIMON = 5

# Estado actual de cada componente
estado_torretas = [90 for _ in torretas]  # Asume centro en 90°
estado_timon = 90  # Asume centro en 90°

# Mapas de teclas
mapa_torretas = {
    '1': (0, -INCREMENTO_TORRETA),
    '2': (0, INCREMENTO_TORRETA),
    'q': (1, -INCREMENTO_TORRETA),
    'w': (1, INCREMENTO_TORRETA),
    'a': (2, -INCREMENTO_TORRETA),
    's': (2, INCREMENTO_TORRETA),
    'z': (3, -INCREMENTO_TORRETA),
    'x': (3, INCREMENTO_TORRETA),
}

FLECHA_IZQ = '\x1b[d'
FLECHA_DER = '\x1b[c'
FLECHA_ARR = '\x1b[a'
FLECHA_ABA = '\x1b[b'

# Para detectar si una tecla está presionada continuamente
try:
    import select
except ImportError:
    select = None

def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
        if ch == '\x1b':
            ch += sys.stdin.read(2)  # Leer secuencia de flecha
        return ch
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)

def main():
    global estado_torretas, estado_timon
    print("Control manual: presiona teclas según el mapeo. Ctrl+C para salir.")
    print("Si mantienes presionada una tecla, el movimiento será continuo.")
    motor = motores_brushless[0]
    try:
        while True:
            tecla = getch().lower()
            # Movimiento continuo mientras la tecla esté presionada
            while True:
                accion_realizada = False
                if tecla in mapa_torretas:
                    idx, delta = mapa_torretas[tecla]
                    if idx < len(torretas):
                        estado_torretas[idx] += delta
                        torretas[idx].girar(estado_torretas[idx])
                        accion_realizada = True
                elif tecla == FLECHA_IZQ:
                    estado_timon -= INCREMENTO_TIMON
                    timones[0].establecer_angulo(estado_timon)
                    accion_realizada = True
                elif tecla == FLECHA_DER:
                    estado_timon += INCREMENTO_TIMON
                    timones[0].establecer_angulo(estado_timon)
                    accion_realizada = True
                elif tecla == FLECHA_ARR:
                    motor.subir_nivel()
                    accion_realizada = True
                elif tecla == FLECHA_ABA:
                    motor.bajar_nivel()
                    accion_realizada = True
                elif tecla == '\x03':  # Ctrl+C
                    print("\nSaliendo...")
                    return
                else:
                    if not accion_realizada:
                        print(f"Tecla no asignada: {repr(tecla)}")
                # Si la tecla sigue presionada, repetir acción
                if select:
                    dr, _, _ = select.select([sys.stdin], [], [], 0.08)
                    if dr:
                        tecla2 = sys.stdin.read(1)
                        if tecla2 == '\x1b':
                            tecla2 += sys.stdin.read(2)
                        if tecla2.lower() == tecla:
                            continue  # Mantener acción
                        else:
                            tecla = tecla2.lower()
                            break
                    else:
                        break
                else:
                    time.sleep(0.08)
                    break
    except KeyboardInterrupt:
        print("\nSaliendo...")

if __name__ == "__main__":
    main()
