class PrivacyOption:
    PRIVATE_BUSY = "private busy"
    PRIVATE_SHOWN = "private shown"
    PUBLIC = "public"
    OPTIONS = {PUBLIC: 0, PRIVATE_SHOWN: 1, PRIVATE_BUSY: 2}
    LOOK_UP = {0: PUBLIC, 1: PRIVATE_SHOWN, 2: PRIVATE_BUSY}

class Privacy:
    PUBLIC = 0
    PRIVATE_SHOWN = 1
    PRIVATE_BUSY = 2
    LOOK_UP = {0: "public", 1: "private shown", 2: "private busy"}

