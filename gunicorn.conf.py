import os

bind = os.environ.get("BIND", "0.0.0.0:5050")
workers = int(os.environ.get("WORKERS", 4))
threads = int(os.environ.get("THREADS", 4))
worker_class = "gthread"
timeout = 120
keepalive = 5
loglevel = "info"
accesslog = "-"
errorlog = "-"
