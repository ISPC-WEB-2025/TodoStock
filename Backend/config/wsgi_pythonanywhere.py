"""
Configuración WSGI para despliegue en PythonAnywhere.

Instrucciones de uso en PythonAnywhere:
1. En la pestaña "Web" de PythonAnywhere, hacer clic en el enlace del archivo WSGI:
   /var/www/<tu_usuario>_pythonanywhere_com_wsgi.py
2. Reemplazar el contenido completo de dicho archivo por el contenido de esta plantilla.
3. Asegurarse de cambiar '<tu_usuario>' por tu nombre de usuario real en PythonAnywhere.
"""

import os
import sys

# Ruta absoluta al directorio Backend dentro del repositorio clonado
# Reemplazá 'tu_usuario' con tu nombre de usuario exacto de PythonAnywhere
path = os.path.expanduser('~/CodeLab/Backend')
if path not in sys.path:
    sys.path.append(path)

# Establecer el módulo de configuración de Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'

# Inicializar la aplicación WSGI
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
