import os

def setup_boat():
    print("--- Configuración Inicial del Barco ---")
    print("Este script configurará las credenciales de conexión segura.")
    
    boat_id = input("Ingrese el BOAT_ID (ej: boat-1): ").strip()
    token = input("Ingrese el TOKEN (copiado del Dashboard): ").strip()
    signaling_url = input("Ingrese la URL del Servidor (default: ws://localhost:8000/ws/): ").strip()
    
    if not signaling_url:
        signaling_url = "ws://localhost:8000/ws/"
        
    # Validar formato básico
    if not boat_id.startswith("boat-"):
        print("Advertencia: El BOAT_ID debería empezar con 'boat-'")
        
    # Guardar en .env
    env_content = f"""SIGNALING_URL={signaling_url}{boat_id}
BOAT_ID={boat_id}
BOAT_TOKEN={token}
"""
    
    with open(".env", "w") as f:
        f.write(env_content)
        
    print("\n--- Configuración Guardada Exitosamente ---")
    print("Archivo .env creado/actualizado.")
    print("Ahora puede ejecutar main.py o boat_client.py")

if __name__ == "__main__":
    setup_boat()
