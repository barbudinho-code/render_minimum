import sys
sys.path.insert(0, '.')
from app import app as application

# O WSGI application está pronto para Gunicorn ou qualquer servidor WSGI
# Não use application.run() aqui - isso inicia o development server do Flask
