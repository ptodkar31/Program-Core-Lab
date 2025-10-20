from multiprocessing.managers import BaseManager
from datetime import datetime

class DSMManager(BaseManager):
    pass

DSMManager.register('state')  # same name as server registration

if __name__ == "__main__":
    mgr = DSMManager(address=("127.0.0.1", 13002), authkey=b'secret')
    mgr.connect()
    state = mgr.state()  # proxy
    now = datetime.now().isoformat()
    new_count = state.inc(1)
    state.append(f"client update at {now}")
    snapshot = state.get()
    print("Counter:", new_count)
    print("Snapshot:", snapshot)
