import json
import pandas as pd
import requests
import time
import datetime


#wallet address and api variables
wallet_address = 'bc1q4fdqv7z8mqk73rtgzk7qdxnzw675320gjar6xx'
api_url = 'https://blockchain.info'
api_end_point = 'rawaddr'
url = f'{api_url}/{api_end_point}/{wallet_address}'
response = requests.get(url)

if response.status_code == 200:
    response_body = response.json()
    TX_COUNT = response_body['n_tx']
    ITERATIONS = int(TX_COUNT / 100) - 1
else:
    ITERATIONS = 0 


##fetching wallet transactions from api
transactions_df = None
i = 0
offset = 0
delay_value = 30
while i <= ITERATIONS:
    url = f'{api_url}/{api_end_point}/{wallet_address}?format=json&offset={offset}'
    print(f'requesting: {url}')
    wallet = pd.read_json(url)
    transactions_df = wallet['txs']
    transactions_df.to_json(f'data/{wallet_address}tx{offset}.json')
    i = i + 1
    offset = offset + 100
    time.sleep(delay_value)


##generating out transactions
i = 0
out_transactions_data = []
while i <= ITERATIONS:
    f_name = f'data/{wallet_address}tx{i*100}.json'
    print(f'opeing file {f_name}')
    file = open(f_name, 'r')
    txs = json.load(file)
    
    for index in txs:
        tx = txs[index]
        tx_hash = tx['hash']
        tx_time = datetime.datetime.fromtimestamp(tx['time'])
        inputs = tx['inputs']
        outs = tx['out']
        is_out_tx = False
        tx_amount = 0

        for input in inputs:
            prev = input['prev_out']
            if prev['addr'] == wallet_address:
                is_out_tx= True

        if is_out_tx:
            out_tx = outs[0]
            tx_amount = float(out_tx['value']) * 0.00000001
            out_tx_address = out_tx['addr']
            out_transactions_data.append([tx_hash, tx_time, wallet_address, tx_amount, out_tx_address])
    i = i + 1

#saving the result to csv file and printing the sum of all outgoing transactions.
result = pd.DataFrame(out_transactions_data, columns=['tx_hash', 'tx_date_time', 'from_addr', 'amount', 'to_addr'])
print(f"Total out amount: {result['amount'].sum()}")
result.to_csv(f'{wallet_address}_out_trx_data.csv', sep=';', index=False)