# JARVIS Gunicorn Production Configuration
# Configuração de produção para Gunicorn

# Server socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker processes
workers = 4
worker_class = "eventlet"  # Para suporte ao SocketIO
worker_connections = 1000
timeout = 30
keepalive = 2

# Restart workers after this many requests, to help prevent memory leaks
max_requests = 1000
max_requests_jitter = 100

# Logging
accesslog = "logs/access.log"
errorlog = "logs/error.log"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s"'

# Process naming
proc_name = "jarvis-web"

# Security
limit_request_line = 4096
limit_request_fields = 100
limit_request_field_size = 8190

# SSL (descomente se usar HTTPS)
# keyfile = "ssl/private.key"
# certfile = "ssl/certificate.crt"