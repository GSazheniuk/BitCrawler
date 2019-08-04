import SharedData
import Waiters

from RTimer import RepeatedTimer
from FrontServer import FrontWatchServer


def process_queue():
    if SharedData.can_process and len(SharedData.queue) > 0:
        SharedData.can_process = False
        current_id = next(iter(SharedData.queue))
        Waiters.all_waiters.deliver_to_waiter(Waiters.WAIT_FOR_QUEUE
                                              , {
                                                  "status": "QUEUED"
                                                  , "wallet": {"address": current_id}
                                              })
        raw_wallet = SharedData.get_raw_wallet(current_id)
        if raw_wallet:
            SharedData.analyze_wallet(raw_wallet)
            res = {
                "wallet": SharedData.wallets[current_id],
                "status": "DONE"
            }
            Waiters.all_waiters.deliver_to_waiter(Waiters.WAIT_FOR_QUEUE, res)
        else:
            res = {
                "wallet": {"address": current_id},
                "status": "ERROR"
            }
            Waiters.all_waiters.deliver_to_waiter(Waiters.WAIT_FOR_QUEUE, res)

        SharedData.queue.remove(current_id)
        SharedData.can_process = True


def save_result():
    SharedData.save_wallets()
    pass


if __name__ == '__main__':
    try:
        SharedData.load_wallets()
        SharedData.start_process()
        rt = RepeatedTimer(2, process_queue)
        rt2 = RepeatedTimer(60, save_result)
        fws = FrontWatchServer()
        fws.run()
    except KeyboardInterrupt:
        print('Goodbye.')
