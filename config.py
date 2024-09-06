from typing import Tuple

class Config:
    """
    Configuration class for MatiksBot.
    """
    url: str = "https://www.matiks.in/"
    botspeed_minmax: Tuple[int, int] = (0.8, 1.5)
    headless_browser = False
    pageload_waittime = 10