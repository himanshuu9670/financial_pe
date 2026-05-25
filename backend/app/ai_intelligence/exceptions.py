"""AI intelligence layer errors — decoupled from HTTP."""


class AiIntelligenceError(Exception):
    """Base error for AI pipeline failures."""


class AiNoTransactionsError(AiIntelligenceError):
    """Statement has no parsed transactions for AI analysis."""


class AiCacheError(AiIntelligenceError):
    """Failed to load or persist AI cache metadata."""
