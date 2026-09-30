from datetime import datetime, timezone
from ..enums import GreenHeatButtonType, GreenHeatEventType
import json

class GreenHeatMessage:
    mobile: bool
    x: float
    y: float
    button: GreenHeatButtonType
    shift: bool
    ctrl: bool
    alt: bool
    time: datetime
    latency: int
    type: GreenHeatEventType
    id: str
    is_anonymous: bool
    latency_ms: int

    raw: str

    def __init__(self, data: dict | str | bytes):
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        if isinstance(data, str):
            self.raw = data
            data = json.loads(data)
        else:
            self.raw = json.dumps(data)

        data["button"] = GreenHeatButtonType(data["button"])
        data["type"] = GreenHeatEventType(data["type"])
        data["time"] = datetime.fromtimestamp(data["time"] / 1000, tz=timezone.utc)

        self.__dict__.update(data)

    @property
    def twitch_id(self) -> str:
        """Returns the Twitch Id of the user, or empty string if anonymous or test UI"""
        if self.is_anonymous or self.id.startswith("U"):
            return ""
        return self.id

    def is_in_box(self, x1: float, y1: float, x2: float, y2: float) -> bool:
        return x2 > self.x > x1 and y2 > self.y > y1

    def is_in_circle(self, center_x: float, center_y: float, radius: float) -> bool:
        dx = self.x - center_x
        dy = self.y - center_y
        return dx * dx + dy * dy <= radius * radius

    def screen_position(self, width: int, height: int) -> tuple[int, int]:
        return int(width * self.x), int(height * self.y)

    @property
    def position(self) -> tuple[float, float]:
        return self.x, self.y

    def distance_from_position(self, x: float, y: float) -> float:
        distance = ((x - self.x) ** 2 + (y - self.y) ** 2) ** 0.5
        return distance

    def to_dict(self):
        return json.loads(self.raw)

    def __str__(self):
        return self.raw

    def __repr__(self):
        return f"GreenHeatMessage({self.id},{self.type},{self.x},{self.y})"
