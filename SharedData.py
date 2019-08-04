import requests
import config
import csv
import os

from datetime import datetime


can_process = True
queue = set()
wallets = {}


def start_process():
    block = get_block()
    analyze_block(block)
    print(wallets)
    pass


def load_wallets():
    if os.path.exists("wallets.csv"):
        with open("wallets.csv", mode="r") as file:
            r = csv.DictReader(file)
            for wallet in r:
                wallets[wallet["address"]] = {
                    'address': wallet['address'],
                    'n_tx': wallet['n_tx'],
                    't_r': wallet['t_r'],
                    't_s': wallet['t_s'],
                    'b': float(wallet['b']),
                    'lt': wallet["lt"],
                }


def save_wallets():
    with open("wallets.csv", mode="w", newline='') as file:
        data = [wallets[w] for w in wallets.copy() if wallets[w]['b'] > 0]
        if len(data) < 1:
            return
        w = csv.DictWriter(file, [header for header in data[0]])
        w.writeheader()
        w.writerows(data)
        print(len(data), " wallets saved. ", len(queue), " in queue.")
        pass


def get_address_list():
    return [wallets[addr] for addr in wallets]


def get_block():
    req = requests.get(config.BC_REQUEST_LATEST_BLOCK_URL)
    latest_block = req.json()
    block_id = latest_block['hash']

    try:
        req = requests.get(config.BC_REQUEST_RAW_BLOCK_URL+block_id)
        block = req.json()
        return block
    except ValueError:
        return None
    pass


def analyze_block(block):
    for t in block['tx']:
        for ins in t['inputs']:
            if 'prev_out' not in ins:
                continue
            if 'addr' not in ins['prev_out']:
                continue

            new_addr = ins['prev_out']['addr']
            if new_addr not in queue and new_addr not in wallets:
                queue.add(new_addr)
                pass
            pass

        for outs in t['out']:
            if 'addr' not in outs:
                continue
            new_addr = outs['addr']
            if new_addr not in queue and new_addr not in wallets:
                queue.add(new_addr)
                pass
            pass
        pass
    pass


def get_raw_wallet(addr):
    try:
        req = requests.get(config.BC_REQUEST_RAW_ADDR_URL+addr)
        wallet = req.json()
        return wallet
    except (ValueError, requests.ConnectionError, requests.exceptions.ChunkedEncodingError) as err:
        print(addr, '<----- ERROR GETTING RAW ADDRESS DATA!!!! - ', err)
        return None
    pass


def analyze_wallet(w_raw):
    w = {
        'address': w_raw['address'],
        'n_tx': w_raw['n_tx'],
        't_r': w_raw['total_received'],
        't_s': w_raw['total_sent'],
        'b': float(w_raw['final_balance']),
        'lt': datetime.fromtimestamp(int(w_raw['txs'][0]['time'])).strftime('%Y-%m-%d %H:%M:%S'),
    }

    wallets[w_raw['address']] = w
    # Go through the list of transactions
    for trn in w_raw['txs']:
        if 'inputs' not in trn:
            continue
        # Analyze 'inputs'
        for inp in trn['inputs']:
            if 'prev_out' not in inp:
                continue
            if 'addr' in inp['prev_out']:
                new_addr = inp['prev_out']['addr']
                if new_addr not in queue and new_addr not in wallets:
                    queue.add(new_addr)
                    pass
                pass
            pass

        # Analyze 'out'-s
        for outp in trn['out']:
            if 'addr' not in outp or outp['value'] == 0:
                continue
            new_addr = outp['addr']
            if new_addr not in queue and new_addr not in wallets:
                queue.add(new_addr)
                pass
            pass
        pass
    pass
