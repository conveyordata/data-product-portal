from __future__ import annotations


class Singleton(type):
    _instances: dict[Singleton, Singleton] = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    def deregister(cls):
        if cls in cls._instances:
            del cls._instances[cls]
        else:
            raise KeyError(f"{cls.__name__} is not registered in {cls._instances}")
