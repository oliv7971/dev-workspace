from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ConvergenceMeasurement:
    date: str
    bg: Optional[float] = None
    hg: Optional[float] = None
    hd: Optional[float] = None
    bd: Optional[float] = None
    lh: Optional[float] = None
    lb: Optional[float] = None

class Convergence:
    def __init__(self):
        self.measurements: List[ConvergenceMeasurement] = []

    def add_measurement(self, measurement: ConvergenceMeasurement):
        self.measurements.append(measurement)

    def get_latest_measurement(self) -> Optional[ConvergenceMeasurement]:
        if self.measurements:
            return self.measurements[-1]
        return None

    def calculate_periodic_change(self) -> Optional[float]:
        if len(self.measurements) < 2:
            return None
        latest = self.measurements[-1]
        previous = self.measurements[-2]
        return (latest.bg - previous.bg) if latest.bg is not None and previous.bg is not None else None

    def calculate_cumulative_change(self) -> Optional[float]:
        if not self.measurements:
            return None
        return self.measurements[-1].bg if self.measurements[-1].bg is not None else None