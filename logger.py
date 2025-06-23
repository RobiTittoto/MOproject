# log.py
LOG_ENABLED = True

def log(*args, **kwargs):
    if LOG_ENABLED:
        print(*args, **kwargs)
