class Positions:
    ORIGIN = (0, 0)

    TEMP_IN = (25, 30)
    TEMP_OUT = (25, 38)
    TEMP_MIN = (25, 46)
    TEMP_MAX = (25, 54)

    HUMID_IN = (92, 30)
    HUMID_OUT = (92, 38)
    HUMID_MIN = (92, 46)
    HUMID_MAX = (92, 54)


def get(name: str):
    return getattr(Positions, name)
