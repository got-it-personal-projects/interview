from gevent.pywsgi import WSGIServer
from app import create_app


http_server = WSGIServer(("", 5000), create_app())
http_server.serve_forever()
