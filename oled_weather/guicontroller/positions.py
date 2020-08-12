class Positions:
    ORIGIN = (0, 0)

    TEMP_IN = (24, 30)
    TEMP_OUT = (24, 38)
    TEMP_MIN = (24, 46)
    TEMP_MAX = (24, 54)

    HUMID_IN = (91, 30)
    HUMID_OUT = (91, 38)
    HUMID_MIN = (91, 46)
    HUMID_MAX = (91, 54)


def get(name: str):
    return getattr(Positions, name)
