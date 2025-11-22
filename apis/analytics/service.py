"""
Service untuk mendapatkan analytics data dari conversation
"""
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session, joinedload
from database.models.session_conversation import SessionConversation, ConversationRole
from database.models.session import Session as SessionModel
from datetime import datetime, timedelta, timezone


class AnalyticsService:
    """Service untuk analytics dan statistics"""

    @staticmethod
    def get_screen_navigation_stats(
        user_id: Optional[str] = None,
        days: int = 30,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Mendapatkan statistik navigasi screen dari conversation

        Args:
            user_id: Optional user_id untuk filter per user
            days: Jumlah hari ke belakang untuk analytics (default 30)
            db: Database session

        Returns:
            Dict containing:
            - total_conversations: Total percakapan
            - total_navigations: Total navigasi yang terjadi
            - screen_stats: List screen dengan jumlah navigasi
            - daily_stats: Statistik harian
        """
        # Calculate date range
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        # Build query
        query = db.query(SessionConversation).filter(
            SessionConversation.created_at >= start_date,
            SessionConversation.created_at <= end_date,
            SessionConversation.role == ConversationRole.ai,
            SessionConversation.response_json.isnot(None)
        ).options(
            joinedload(SessionConversation.session).joinedload(SessionModel.user)
        )

        # Filter by user if provided
        if user_id:
            query = query.join(SessionConversation.session).filter(
                SessionModel.user_id == user_id
            )

        # Get all AI conversations with response_json
        conversations = query.order_by(SessionConversation.created_at.desc()).all()

        # Process statistics
        total_conversations = len(conversations)
        screen_navigation_count = {}
        screen_details = {}
        daily_navigation = {}
        total_navigations = 0

        for conv in conversations:
            response_json = conv.response_json

            if isinstance(response_json, dict):
                # Get navigation object from response_json
                navigation = response_json.get("navigation")

                # Fallback: support old format with selected_screen_key
                old_format_key = response_json.get("selected_screen_key")

                # Check if navigation exists and is not null
                if navigation and isinstance(navigation, dict):
                    total_navigations += 1

                    # Extract screen info from navigation object
                    screen_id = navigation.get("screen_id")
                    screen_name = navigation.get("screen_name", screen_id)
                    deep_link = navigation.get("deep_link", "")

                    if not screen_id:
                        continue

                # Handle old format (backward compatibility)
                elif old_format_key and old_format_key != "null" and old_format_key is not None:
                    total_navigations += 1

                    # Use old format key as screen_id
                    screen_id = old_format_key
                    screen_name = old_format_key  # No screen name in old format
                    deep_link = ""  # No deep link in old format

                else:
                    # No navigation in this conversation
                    continue

                # Count screen navigation
                if screen_id not in screen_navigation_count:
                    screen_navigation_count[screen_id] = 0
                    screen_details[screen_id] = {
                        "screen_id": screen_id,
                        "screen_name": screen_name,
                        "deep_link": deep_link,
                        "count": 0,
                        "last_accessed": None
                    }

                screen_navigation_count[screen_id] += 1
                screen_details[screen_id]["count"] += 1

                # Update last accessed
                if (screen_details[screen_id]["last_accessed"] is None or
                    conv.created_at > screen_details[screen_id]["last_accessed"]):
                    screen_details[screen_id]["last_accessed"] = conv.created_at

                # Daily statistics
                date_key = conv.created_at.strftime("%Y-%m-%d")
                if date_key not in daily_navigation:
                    daily_navigation[date_key] = 0
                daily_navigation[date_key] += 1

        # Sort screens by count (descending)
        screen_stats = sorted(
            screen_details.values(),
            key=lambda x: x["count"],
            reverse=True
        )

        # Format daily stats
        daily_stats = [
            {"date": date, "count": count}
            for date, count in sorted(daily_navigation.items())
        ]

        return {
            "total_conversations": total_conversations,
            "total_navigations": total_navigations,
            "navigation_rate": round(total_navigations / total_conversations * 100, 2) if total_conversations > 0 else 0,
            "screen_stats": screen_stats,
            "daily_stats": daily_stats,
            "date_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "days": days
            }
        }

    @staticmethod
    def get_conversation_insights(
        user_id: Optional[str] = None,
        days: int = 30,
        db: Session = None
    ) -> Dict[str, Any]:
        """
        Mendapatkan insights dari conversation (language usage, etc)

        Args:
            user_id: Optional user_id untuk filter per user
            days: Jumlah hari ke belakang
            db: Database session

        Returns:
            Dict containing insights data
        """
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=days)

        # Build query
        query = db.query(SessionConversation).filter(
            SessionConversation.created_at >= start_date,
            SessionConversation.created_at <= end_date
        ).options(
            joinedload(SessionConversation.session)
        )

        # Filter by user if provided
        if user_id:
            query = query.join(SessionConversation.session).filter(
                SessionModel.user_id == user_id
            )

        conversations = query.all()

        total = len(conversations)
        user_messages = sum(1 for c in conversations if c.role == ConversationRole.user)
        ai_messages = sum(1 for c in conversations if c.role == ConversationRole.ai)

        return {
            "total_conversations": total,
            "user_messages": user_messages,
            "ai_messages": ai_messages,
            "unique_sessions": len(set(c.session_id for c in conversations))
        }
