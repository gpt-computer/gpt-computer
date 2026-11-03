"""
AI Error Definitions

This module provides error classes for the AI client layer.

Classes:
    GPTCError: Base exception for all AI client-related errors.
    ProviderNotFoundError: Raised when a provider is not found.
    ProviderNotWorkingError: Raised when the provider is unavailable or failing.
    StreamNotSupportedError: Raised when the requested provider does not support streaming.
    ModelNotFoundError: Raised when a model is not found.
    ModelNotAllowedError: Raised when a model is not allowed by configuration or policy.
    RetryProviderError: Raised to retry with another provider.
    RetryNoProviderError: Raised when there are no providers left to retry.
    VersionNotFoundError: Raised when the version could not be determined.
    MissingRequirementsError: Raised when a required dependency is missing.
    NestAsyncioError: Raised when 'nest_asyncio2' is missing.
    MissingAuthError: Raised when authentication details are missing.
    PaymentRequiredError: Raised when a provider requires payment before access.
    NoMediaResponseError: Raised when a media request returns no response.
    ResponseError: Base class for response-related errors.
    ResponseStatusError: Raised when an HTTP response returns a non-success status code.
    CloudflareError: Raised when a request is blocked by Cloudflare.
    BadRequestError: Raised when a request is malformed or invalid.
    RateLimitError: Raised when the provider's rate limit has been exceeded.
    NoValidHarFileError: Raised when no valid HAR file is found.
    TimeoutError: Raised for timeout errors during API requests.
    ConversationLimitError: Raised when a conversation limit is reached on the provider.
    ProviderException: Raised for general provider-related exceptions.
"""


class GPTCError(Exception):
    """Base exception for all AI client-related errors."""

    pass


class ProviderNotFoundError(GPTCError):
    """Raised when a provider is not found."""

    pass


class ProviderNotWorkingError(GPTCError):
    """Raised when the provider is unavailable or failing."""

    pass


class StreamNotSupportedError(GPTCError):
    """Raised when the requested provider does not support streaming."""

    pass


class ModelNotFoundError(GPTCError):
    """Raised when a model is not found."""

    pass


class ModelNotAllowedError(GPTCError):
    """Raised when a model is not allowed by configuration or policy."""

    pass


class RetryProviderError(GPTCError):
    """Raised to retry with another provider."""

    pass


class RetryNoProviderError(GPTCError):
    """Raised when there are no providers left to retry."""

    pass


class VersionNotFoundError(GPTCError):
    """Raised when the version could not be determined."""

    pass


class MissingRequirementsError(GPTCError):
    """Raised when a required dependency is missing."""

    pass


class NestAsyncioError(MissingRequirementsError):
    """Raised when 'nest_asyncio2' is missing."""

    pass


class MissingAuthError(GPTCError):
    """Raised when authentication details are missing."""

    pass


class PaymentRequiredError(GPTCError):
    """Raised when a provider requires payment before access."""

    pass


class NoMediaResponseError(GPTCError):
    """Raised when a media request returns no response."""

    pass


class ResponseError(GPTCError):
    """Base class for response-related errors."""

    pass


class ResponseStatusError(ResponseError):
    """Raised when an HTTP response returns a non-success status code."""

    pass


class CloudflareError(ResponseStatusError):
    """Raised when a request is blocked by Cloudflare."""

    pass


class BadRequestError(ResponseStatusError):
    """Raised when a request is malformed or invalid."""

    pass


class RateLimitError(ResponseStatusError):
    """Raised when the provider's rate limit has been exceeded."""

    pass


class NoValidHarFileError(GPTCError):
    """Raised when no valid HAR file is found."""

    pass


class TimeoutError(GPTCError):
    """Raised for timeout errors during API requests."""

    pass


class ConversationLimitError(GPTCError):
    """Raised when a conversation limit is reached on the provider."""

    pass


class ProviderException(GPTCError):
    """Raised for general provider-related exceptions."""

    pass
