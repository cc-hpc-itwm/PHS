import os
from dask.distributed import Client, as_completed

def task(hyperpar):
    exec(hyperpar, globals(), globals())
    result = x * y
    return result

DASK_MASTER_IP = os.environ['DASK_MASTER_IP']
DASK_MASTER_PORT = os.environ['DASK_MASTER_PORT']
sub_future = []
parameter_string_list = ['x=1\ny=2','x=2\ny=4','x=3\ny=6']
with Client(DASK_MASTER_IP + ':' + DASK_MASTER_PORT, timeout='20s') as client:
    #client.upload_file('/home/HabelitzP/phs/test_functions.py')
    for s in parameter_string_list:
        sub_future.append(client.submit(task, s))
    for f in as_completed(sub_future):
        print(f.result()) # errors occuring during execution of future f inside workers are fetched and reraised with the result() method