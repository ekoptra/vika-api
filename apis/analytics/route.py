"""
Analytics API routes
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from middleware.auth import get_current_user
from database.models.user import User
from database.base import get_db
from apis.analytics.service import AnalyticsService

analytics_router = APIRouter(
    prefix="/api/analytics",
    tags=["Analytics"]
)


@analytics_router.get("/screen-navigation")
def get_screen_navigation_stats(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get screen navigation statistics

    Returns statistics about which screens are most frequently navigated to
    """
    stats = AnalyticsService.get_screen_navigation_stats(
        user_id=current_user.id,
        days=days,
        db=db
    )
    return {
        "success": True,
        "data": stats
    }


@analytics_router.get("/conversation-insights")
def get_conversation_insights(
    days: int = Query(default=30, ge=1, le=365, description="Number of days to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get conversation insights and statistics
    """
    insights = AnalyticsService.get_conversation_insights(
        user_id=current_user.id,
        days=days,
        db=db
    )
    return {
        "success": True,
        "data": insights
    }
