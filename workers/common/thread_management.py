import threading


def run_in_background(func):
    def background_runner(*args, **kwargs):
        thread = threading.Thread(target=func, args=args, kwargs=kwargs)
        thread.start()
    return background_runner