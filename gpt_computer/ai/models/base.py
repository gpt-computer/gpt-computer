"""Compatibility re-export for model base classes."""

from gpt_computer.ai.models.models import (
    AudioModel,
    ImageModel,
    Model,
    ModelRegistry,
    VideoModel,
    VisionModel,
)

__all__ = [
    "AudioModel",
    "ImageModel",
    "Model",
    "ModelRegistry",
    "VideoModel",
    "VisionModel",
]
