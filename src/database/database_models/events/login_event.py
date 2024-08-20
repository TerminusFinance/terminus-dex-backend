from .base_event import BaseEventDb


class LoginEventDb(BaseEventDb):

    __tablename__ = "login_event"

    # === === === Args === === ===
    __mapper_args__ = {
        "polymorphic_identity": "login",
        "concrete": True,
    }
