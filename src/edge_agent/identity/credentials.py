from config.credenciales import eliminar_identidad, guardar_identidad, obtener_identidad


def load_identity():
    return obtener_identidad()


def save_identity(num_serie: str, token: str) -> bool:
    return guardar_identidad(num_serie, token)


def reset_identity() -> None:
    eliminar_identidad()
