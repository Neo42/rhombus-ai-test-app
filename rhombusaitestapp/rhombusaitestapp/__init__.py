"""Initialization for the RhombusAI Test App."""

from .celery import app as celery_app

__all__ = ("celery_app",)
