"""
This module defines FastAPI endpoints for system-related functionalities.

It provides routes for:
- Checking the operational status of the API.
- Retrieving public configuration settings of the API.
"""
# src/backend_projeto/api/system_endpoints.py
from fastapi import APIRouter, Depends
from typing import Dict, Any
from backend_projeto.utils.config import Settings
from .deps import get_config

router = APIRouter(
    tags=["System"],
    responses={404: {"description": "Not found"}},
)

@router.get("/status")
def status() -> Dict[str, str]:
    """
    Checks if the API is online and operational.

    Returns:
        Dict[str, str]: A dictionary with a "status" key, indicating "ok" if the API is running.
    """
    return {"status": "ok"}

@router.get("/config")
def get_public_config(config: Settings = Depends(get_config)) -> Dict[str, Any]:
    """
    Returns public configuration settings of the API.

    Args:
        config (Settings): Dependency injection for application settings.

    Returns:
        Dict[str, Any]: A dictionary containing public configuration parameters.
    """
    return config.to_dict()
