from common.socketio import sio
from database.base import SessionLocal
from database.models.session import Session as SessionModel
from datetime import datetime

@sio.event
async def connect(sid, environ, auth):
  """
  Handle client connection

  Args:
    sid: Socket ID
    environ: WSGI environ dict
    auth: Authentication data (harus berisi session_id)
  """
  print(f"🔌 Client connecting: {sid}")

  # Validate auth data
  if not auth or 'session_id' not in auth:
    print(f"❌ Connection rejected: No session_id provided")
    return False

  session_id = auth['session_id']

  # Validate session exists in database
  db = SessionLocal()
  try:
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()

    if not session:
      print(f"❌ Connection rejected: Invalid session_id {session_id}")
      return False

    # Check if session expired
    if session.expired_at < datetime.now():
      print(f"❌ Connection rejected: Session expired {session_id}")
      return False

    # Join room with session_id
    await sio.enter_room(sid, session_id)

    print(f"✅ Client connected: {sid} → Room: {session_id}")

    # Send welcome message
    await sio.emit('connected', {
      'status': 'connected',
      'session_id': session_id,
      'message': 'Successfully connected to Socket.IO'
    }, room=sid)

    return True

  except Exception as e:
    print(f"❌ Error during connection: {e}")
    return False

  finally:
    db.close()


@sio.event
async def disconnect(sid):
  print(f"🔌 Client disconnected: {sid}")


@sio.event
async def ping(sid, data):
  await sio.emit('pong', {'message': 'pong', 'timestamp': datetime.now().isoformat()}, room=sid)


async def emit_to_session(session_id: str, event: str, data: dict):
  """
  Emit event ke specific session room

  Args:
    session_id: Session ID (room identifier)
    event: Event name
    data: Event data
  """
  try:
    await sio.emit(event, data, room=session_id)
    print(f"📤 Emitted '{event}' to session {session_id}")
  except Exception as e:
    print(f"❌ Failed to emit to session {session_id}: {e}")
