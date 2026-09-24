from fastapi import WebSocket


class ConnectionManager:

    def __init__(self):
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(
        self,
        payment_id: int,
        websocket: WebSocket
    ):
        await websocket.accept()

        if payment_id not in self.active_connections:
            self.active_connections[payment_id] = []

        self.active_connections[payment_id].append(websocket)

    def disconnect(
        self,
        payment_id: int,
        websocket: WebSocket
    ):
        if payment_id in self.active_connections:
            self.active_connections[payment_id].remove(websocket)

            if not self.active_connections[payment_id]:
                del self.active_connections[payment_id]

    async def broadcast_to_payment(
        self,
        payment_id: int,
        message: str
    ):
        connections = self.active_connections.get(
            payment_id,
            []
        )

        for connection in connections:
            await connection.send_text(message)


manager = ConnectionManager()