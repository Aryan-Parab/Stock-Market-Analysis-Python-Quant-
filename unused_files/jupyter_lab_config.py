"""
Jupyter Lab Configuration File
Place this in ~/.jupyter/jupyter_lab_config.py or pass via --config flag
"""

# Enable SSL/TLS for secure connections
c.ServerApp.certfile = '/app/certs/jupyter.pem'
c.ServerApp.keyfile = '/app/certs/jupyter.key'

# Allow connections from any IP (useful in Docker)
c.ServerApp.ip = '0.0.0.0'
c.ServerApp.port = 8888
c.ServerApp.allow_root = True

# Disable token authentication for local development
# (enable for production with proper authentication)
c.ServerApp.token = ''
c.ServerApp.password = ''

# Enable CORS for cross-origin requests
c.ServerApp.disable_check_xsrf = True

# Jupyter Lab specific settings
c.LabApp.open_browser = False

# Log level
c.Application.log_level = 'INFO'
