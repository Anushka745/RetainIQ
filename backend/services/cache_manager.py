"""
services/cache_manager.py
Simple in-memory cache manager for caching churn predictions per account/owner.
"""

import logging

logger = logging.getLogger("retainiq.cache_manager")

# In-memory cache mapping owner_id -> (prediction_df, accuracy)
_churn_cache = {}


def get_cached_churn(owner_id: int):
    """Retrieve cached churn predictions and accuracy for a specific owner."""
    return _churn_cache.get(owner_id)


def set_cached_churn(owner_id: int, df, accuracy: float):
    """Store churn predictions and accuracy in cache for a specific owner."""
    _churn_cache[owner_id] = (df, accuracy)
    logger.info("Cached churn predictions for owner_id=%s", owner_id)


def invalidate_churn_cache(owner_id: int = None):
    """Invalidate churn predictions cache for a specific owner or all owners."""
    global _churn_cache
    if owner_id is not None:
        if owner_id in _churn_cache:
            del _churn_cache[owner_id]
            logger.info("Invalidated churn cache for owner_id=%s", owner_id)
    else:
        _churn_cache.clear()
        logger.info("Invalidated entire churn cache")
