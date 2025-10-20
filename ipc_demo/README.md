# IPC Demo – Sockets, Distributed Shared Memory, and RPC

Run commands in PowerShell from this folder.

TCP message passing (echo):
1) python ".\tcp_server.py"
2) python ".\tcp_client.py"  (type lines, Ctrl+C to exit)

UDP message passing (echo):
1) python ".\udp_server.py"
2) python ".\udp_client.py"  (type lines, Ctrl+C to exit)

Distributed Shared Memory (DSM) via multiprocessing.managers:
1) python ".\dsm_server.py"
2) python ".\dsm_client.py"  (run multiple times; it increments a shared counter and appends a message)

RPC system (JSON over TCP):
1) python ".\rpc_server.py"
2) python ".\rpc_client.py"  (demo + interactive: call add, mul, echo, time, quit)
