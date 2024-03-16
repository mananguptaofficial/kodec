import time
import blocksmith
import pandas as pd
import requests
import multiprocessing
from multiprocessing import cpu_count, Value
from rich.console import Console
from lxml import html

console = Console()
console.clear()

def fetch_balance(address):
    url = "https://bitcoin.atomicwallet.io/address/" + address
    response = requests.get(url)
    if response.status_code == 200:
        tree = html.fromstring(response.content)
        balance_element = tree.xpath('/html/body/main/div/div[2]/div[1]/table/tbody/tr[3]/td[2]')
        if balance_element:
            return balance_element[0].text_content().strip()
    return "No data available"

import time

def search_addresses(core_number, winner_file, sert_shared):
    addresses = set(pd.read_csv("btc.txt", header=None).iloc[:, 0])
    w = 0
    while True:
        passphrase = blocksmith.KeyGenerator()
        passphrase.seed_input('qwertyuiopasdfghjklzxcvbnm1234567890')
        private_key = passphrase.generate_key()
        address = blocksmith.BitcoinWallet.generate_address(private_key)
        balance = fetch_balance(address)
        with sert_shared.get_lock():
            sert_shared.value += 1
            sert = sert_shared.value
            if balance != "No data available":
                with open(winner_file, "a") as f:
                    if balance != '0 BTC' or address in addresses:
                        w += 1
                        f.write(f'\nADDR: {address}     BAL: {balance}\nKEY: {private_key}\n------------------------(MMDRZA.COM)---------------------\n')
                    else:
                        console.print(f'[gold1]{sert}[/][green] : {address} : [/][yellow]{private_key}[/][green] :  - B:[/][gold1]{balance}[/][b green]  W:[/][with]{w}[/]')
            else:
                console.print(f'[red]No data available for address:[/][gold1]{address}[/]')
                time.sleep(15)  # Wait for 15 seconds before retrying


if __name__ == '__main__':
    num_cores = 12  # Use 12 cores
    winner_file = "WinnerSmit.txt"
    sert_shared = Value('i', 0)
    jobs = []
    for core_number in range(num_cores):
        p = multiprocessing.Process(target=search_addresses, args=(core_number, winner_file, sert_shared))
        jobs.append(p)
        p.start()
