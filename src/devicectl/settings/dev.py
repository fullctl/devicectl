import logging
import secrets

set_option("SERVER_EMAIL", "root@localhost")
set_from_env("SECRET_KEY", "devicectl-dev-secret-key")
