import threading

from django.conf import settings

_controller = None
_lock = threading.Lock()


def get_controller():
    """Singleton chosen by IOT_MODE ('demo' | 'real')."""
    global _controller
    if _controller is None:
        with _lock:
            if _controller is None:
                if settings.IOT_MODE == "real":
                    from .mqtt_controller import MQTTController
                    _controller = MQTTController()
                else:
                    from .demo_controller import DemoController
                    _controller = DemoController()
    return _controller


def reset_controller():
    global _controller
    _controller = None
