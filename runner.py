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
            SharedData.total_analyzed += 1
            res = {
                "wallet": SharedData.wallets[current_id],
                "status": "DONE"
            }
            Waiters.all_waiters.deliver_to_waiter(Waiters.WAIT_FOR_QUEUE, res)
        else:
            SharedData.total_err += 1
            res = {
                "wallet": {"address": current_id},
                "status": "ERROR"
            }
            Waiters.all_waiters.deliver_to_waiter(Waiters.WAIT_FOR_QUEUE, res)

        SharedData.queue.remove(current_id)
        if SharedData.total_analyzed % 100 == 0:
            SharedData.save_wallets()
            print(SharedData.total_analyzed, " analyzed, "
                  , SharedData.total_err, " errors, "
                  , SharedData.total_saved, " saved, "
                  , len(SharedData.queue), " in queue."
                  )
        SharedData.can_process = True


if __name__ == '__main__':
    try:
        SharedData.load_wallets()
        SharedData.start_process()
        rt = RepeatedTimer(1, process_queue)
        fws = FrontWatchServer()
        fws.run()
    except KeyboardInterrupt:
        print('Goodbye.')
