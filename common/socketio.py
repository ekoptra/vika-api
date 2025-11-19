import socketio

# Create AsyncServer instance
sio = socketio.AsyncServer(
  async_mode='asgi',
  cors_allowed_origins='*',  # Untuk development, di production ganti dengan domain spesifik
  logger=True,
  engineio_logger=False
)

# Create ASGI app
socket_app = socketio.ASGIApp(
  sio,
  socketio_path='/socket.io'
)
