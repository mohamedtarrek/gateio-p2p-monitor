"""
FastAPI router for Gate.io P2P Monitor REST API.
Provides endpoints for settings, status, and control operations.
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from typing import Optional
from datetime import datetime
from app.models import (
    MonitorSettings, StatusResponse, UpdateResponse, 
    SystemStatus, NotificationLog
)
from app.services.monitor_service import monitor
from app.services.telegram_service import telegram_service
from app.utils import setup_logger

logger = setup_logger(__name__)

router = APIRouter(prefix="/api", tags=["monitor"])

@router.post("/settings", response_model=UpdateResponse)
async def update_settings(settings: MonitorSettings):
    """
    Update monitor settings immediately without restarting.
    Validates Telegram token before applying.
    """
    try:
        success = await monitor.update_settings(settings)

        if not success:
            return UpdateResponse(
                success=False,
                message="Failed to update settings",
                error="Invalid Telegram bot token. Please verify your token from @BotFather."
            )

        return UpdateResponse(
            success=True,
            message="Settings updated successfully. Changes take effect immediately.",
            updated_settings=settings
        )

    except Exception as e:
        logger.error(f"Settings update error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status", response_model=StatusResponse)
async def get_status():
    """Get current system status including uptime and last check time."""
    status_data = monitor.get_status()
    return StatusResponse(**status_data)

@router.post("/start")
async def start_monitor():
    """Start the price monitoring service."""
    success = await monitor.start()

    if not success:
        raise HTTPException(
            status_code=400,
            detail="Cannot start monitor. Please configure settings first."
        )

    return {"success": True, "message": "Monitor started successfully", "status": "Running"}

@router.post("/stop")
async def stop_monitor():
    """Stop the price monitoring service."""
    success = await monitor.stop()

    return {"success": True, "message": "Monitor stopped successfully", "status": "Stopped"}

@router.post("/test-telegram")
async def test_telegram(settings: MonitorSettings):
    """
    Send a test message to verify Telegram configuration.
    Does not save settings, just tests connectivity.
    """
    try:
        success = await telegram_service.send_test_message(
            bot_token=settings.telegram_bot_token,
            chat_id=settings.telegram_chat_id
        )

        if success:
            return {"success": True, "message": "Test message sent successfully!"}
        else:
            raise HTTPException(
                status_code=400,
                detail="Failed to send test message. Please check your Bot Token and Chat ID."
            )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_notification_history(limit: int = 50):
    """Get recent notification history."""
    history = monitor.get_notification_history(limit)
    return {
        "notifications": history,
        "total": len(monitor.state.notification_history)
    }

@router.delete("/history")
async def clear_history():
    """Clear all notification history."""
    monitor.clear_history()
    return {"success": True, "message": "Notification history cleared"}

@router.get("/health")
async def health_check():
    """Health check endpoint for Railway and monitoring."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "monitor_status": monitor.state.status.value
    }
