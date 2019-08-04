from tornado.concurrent import Future

WAIT_FOR_QUEUE = 0


class Waiters:
    def __init__(self):
        self._all_waiters = {
            WAIT_FOR_QUEUE: set(),
        }
        pass

    def subscribe_waiter(self, waiter_type):
        result_future = Future()
        self._all_waiters[waiter_type].add(result_future)
        return result_future

    def deliver_to_waiter(self, waiter_type, o):
        for future in list(self._all_waiters[waiter_type]):
            future.set_result(o)
            self._all_waiters[waiter_type].remove(future)
            pass
        pass

    def cancel_waiter(self, waiter_type, future):
        self._all_waiters[waiter_type].remove(future)
        pass


all_waiters = Waiters()
