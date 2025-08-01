from config.componentes import MOTORES_BRUSHLESS, TIMONES, TORRETAS
from controladores.motor_brushless import MotorBrushless
from controladores.timon import Timon
from controladores.torreta import Torreta

motores_brushless = [MotorBrushless(**m) for m in MOTORES_BRUSHLESS]
timones = [Timon(**t) for t in TIMONES]
torretas = [Torreta(**tr) for tr in TORRETAS]
