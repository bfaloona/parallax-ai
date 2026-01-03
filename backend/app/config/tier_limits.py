"""Tier-based token limits configuration.

This module defines monthly token limits for each subscription tier and model.
Limits are enforced per-model to provide granular usage tracking.
"""

from typing import Dict, TypedDict


class TierLimitDict(TypedDict):
    """Type definition for model-specific token limits."""

    haiku: int
    sonnet: int
    opus: int


# Monthly token limits per tier
# Format: tier_name -> {model -> token_limit}
TIER_LIMITS: Dict[str, TierLimitDict] = {
    "free": {
        "haiku": 25_000,
        "sonnet": 0,
        "opus": 0,
    },
    "starter": {
        "haiku": 100_000,
        "sonnet": 50_000,
        "opus": 0,
    },
    "pro": {
        "haiku": 500_000,
        "sonnet": 250_000,
        "opus": 100_000,
    },
    "enterprise": {
        "haiku": 2_000_000,
        "sonnet": 1_000_000,
        "opus": 500_000,
    },
}


def validate_tier(tier: str) -> bool:
    """Validate that a tier exists in the configuration.

    Args:
        tier: Tier name to validate

    Returns:
        True if tier exists, False otherwise
    """
    return tier in TIER_LIMITS


def get_tier_limits(tier: str) -> TierLimitDict:
    """Get token limits for a tier with fallback to free tier.

    Args:
        tier: Tier name

    Returns:
        Dictionary of model token limits
    """
    return TIER_LIMITS.get(tier, TIER_LIMITS["free"])


def get_model_limit(tier: str, model: str) -> int:
    """Get token limit for a specific tier and model.

    Args:
        tier: Tier name
        model: Model name (haiku, sonnet, opus)

    Returns:
        Monthly token limit for the model, or 0 if not found
    """
    tier_limits = get_tier_limits(tier)
    return tier_limits.get(model, 0)  # type: ignore


def get_all_tiers() -> list[str]:
    """Get list of all available tiers.

    Returns:
        List of tier names
    """
    return list(TIER_LIMITS.keys())
