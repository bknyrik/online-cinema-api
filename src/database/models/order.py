from enum import StrEnum, auto


class OrderStatusEnum(StrEnum):
    PENDING = auto()
    PAID = auto()
    CANCELLED = auto()
