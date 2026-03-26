"""Application-wide constants."""

# Ticket categories
CATEGORIES = [
    "billing", "refund", "technical", "account",
    "shipping", "product", "general", "escalation",
]

# Severity levels
SEVERITY = ["low", "medium", "high", "critical"]

# Resolution states
class ResolutionStatus:
    OPEN        = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED    = "resolved"
    ESCALATED   = "escalated"
    FAILED      = "failed"

# Action types
class ActionType:
    RESPOND    = "respond"
    CLASSIFY   = "classify"
    RETRIEVE   = "retrieve"
    ESCALATE   = "escalate"
    RESOLVE    = "resolve"
    CLARIFY    = "clarify"

# Task difficulty
class TaskDifficulty:
    EASY   = "easy"
    MEDIUM = "medium"
    HARD   = "hard"

TASK_IDS = {
    TaskDifficulty.EASY:   "support-easy-v1",
    TaskDifficulty.MEDIUM: "support-medium-v1",
    TaskDifficulty.HARD:   "support-hard-v1",
}
