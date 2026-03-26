"""In-memory metrics collector (Prometheus-compatible labels)."""
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict

@dataclass
class MetricsStore:
    counters: Dict[str, float] = field(default_factory=lambda: defaultdict(float))
    histograms: Dict[str, list] = field(default_factory=lambda: defaultdict(list))

    def inc(self, name: str, value: float = 1.0, **labels):
        key = self._key(name, labels)
        self.counters[key] += value

    def observe(self, name: str, value: float, **labels):
        key = self._key(name, labels)
        self.histograms[key].append(value)

    def get_counter(self, name: str, **labels) -> float:
        return self.counters[self._key(name, labels)]

    def summary(self) -> dict:
        return {
            "counters": dict(self.counters),
            "histogram_means": {
                k: sum(v) / len(v) for k, v in self.histograms.items() if v
            },
        }

    @staticmethod
    def _key(name: str, labels: dict) -> str:
        label_str = ",".join(f"{k}={v}" for k, v in sorted(labels.items()))
        return f"{name}{{{label_str}}}" if label_str else name


METRICS = MetricsStore()
