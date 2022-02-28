# https://docs.gunicorn.org/en/latest/settings.html#accesslog
accesslog = "-"

# https://docs.gunicorn.org/en/latest/settings.html#accesslog
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(M)s'

# https://docs.gunicorn.org/en/latest/settings.html#errorlog
errorlog = "-"

# https://docs.gunicorn.org/en/latest/settings.html#timeout
timeout = 30
