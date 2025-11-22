"""
Quick test script to check navigation parsing
"""
from database.base import SessionLocal
from database.models.session_conversation import SessionConversation, ConversationRole
from sqlalchemy.orm import joinedload
from database.models.session import Session as SessionModel

db = SessionLocal()

# Get one AI conversation with response_json
conv = db.query(SessionConversation).filter(
    SessionConversation.role == ConversationRole.ai,
    SessionConversation.response_json.isnot(None)
).first()

if conv:
    print("✅ Found conversation:")
    print(f"ID: {conv.id}")
    print(f"Role: {conv.role}")
    print(f"\n📄 response_json:")
    print(conv.response_json)
    print(f"\nType: {type(conv.response_json)}")

    if isinstance(conv.response_json, dict):
        print("\n🔍 Checking navigation:")
        navigation = conv.response_json.get("navigation")
        print(f"navigation value: {navigation}")
        print(f"navigation type: {type(navigation)}")
        print(f"navigation is dict: {isinstance(navigation, dict)}")
        print(f"navigation is not None: {navigation is not None}")

        if navigation and isinstance(navigation, dict):
            print("\n✅ Navigation object found!")
            print(f"screen_id: {navigation.get('screen_id')}")
            print(f"screen_name: {navigation.get('screen_name')}")
            print(f"deep_link: {navigation.get('deep_link')}")
        else:
            print("\n❌ Navigation is None or not a dict")
else:
    print("❌ No AI conversation found")

db.close()
