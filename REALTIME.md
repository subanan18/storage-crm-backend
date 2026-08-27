# Realtime CRM updates

The backend now includes a lightweight WebSocket channel system for live dashboard and workflow notifications.

## Connect

```text
ws://localhost:8000/realtime/ws/dashboard
```

Any channel name can be used, for example `dashboard`, `warehouse`, or `project-42`.

After connecting, the server sends a `connected` event. Send the text `ping` to receive a `pong` response with the current connection count.

## Event format

```json
{
  "type": "item.updated",
  "channel": "dashboard",
  "timestamp": "2026-08-27T12:00:00+00:00",
  "payload": {
    "item_id": 123,
    "status": "Stored"
  }
}
```

The `RealtimeHub` is intentionally in-memory for the portfolio version. For horizontal production deployment, it can be replaced by Redis pub/sub while keeping the frontend WebSocket contract unchanged.
