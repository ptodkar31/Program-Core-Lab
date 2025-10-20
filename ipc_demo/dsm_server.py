from multiprocessing.managers import BaseManager
from dataclasses import dataclass
from typing import Any

class SharedState:
    def __init__(self) -> None:
        self.counter = 0
        self.messages = []
    def inc(self, n: int = 1) -> int:
        self.counter += int(n)
        return self.counter
    def append(self, msg: Any) -> int:
        self.messages.append(str(msg))
        return len(self.messages)
    def get(self) -> dict:
        return {"counter": self.counter, "messages": list(self.messages)}

_state = SharedState()

class DSMManager(BaseManager):
    pass

DSMManager.register('state', callable=lambda: _state, exposed=['inc','append','get'])

if __name__ == "__main__":
    print("DSM server on 127.0.0.1:13002 (authkey=b'secret')")
    mgr = DSMManager(address=("127.0.0.1", 13002), authkey=b'secret')
    srv = mgr.get_server()
    srv.serve_forever()
