def safe_read(path):
    try:
        with open(path, 'rb') as fh:
            return fh.read()
    except Exception:
        return None
