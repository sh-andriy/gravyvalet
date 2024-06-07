import enum


class InvocationStatus(enum.Enum):
    STARTING = 1
    GOING = 2
    SUCCESS = 3
    ERROR = 128
