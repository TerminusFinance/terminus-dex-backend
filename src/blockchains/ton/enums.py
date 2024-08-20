from enum import StrEnum


class AccountStatus(StrEnum):
    ACTIVE = "active"
    UNINIT = "uninit"
    NONEXIST = "nonexist"
    FROZEN = "frozen"
