"""Basic analytics aggregation."""
from app.utils.metrics import METRICS


class AnalyticsService:
    def summary(self) -> dict:
        return METRICS.summary()

    def episode_stats(self) -> dict:
        m = METRICS
        return {
            "total_steps":    m.get_counter("env.step"),
            "total_episodes": m.get_counter("env.episode_done"),
            "total_resets":   m.get_counter("env.reset"),
        }
