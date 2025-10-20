# Client-Server Application – How to Run

This folder now contains only documentation with steps to run the project you just tested.

Prerequisites:
- Python 3.x
- PowerShell terminal

Real-time Chat (broadcast to all clients):
1) Start server:
   python ".\client-server application\chat_server.py"
2) Start one or more clients in separate terminals:
   python ".\client-server application\chat_client.py"
3) Type messages; use /quit to exit.

Basic Request/Response RPC demo:
1) Start server:
   python ".\client-server application\server.py"
2) Start client:
   python ".\client-server application\client.py"
3) Try commands in client: ping, echo Hello, sum 1 2 3.5, quit

Protocol notes (for both demos):
- TCP with 4-byte big-endian length prefix + UTF-8 JSON payload per message.
- Request examples:
  {"type":"join","name":"Alice"}  // chat join
  {"type":"msg","text":"hello"}    // chat message
  {"cmd":"ping"}                       // rpc
- Response envelope: {"ok": bool, "data": any, "error": str|null}
