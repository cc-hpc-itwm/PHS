import examples.func_def.basic_test_functions
from dask.distributed import Client, as_completed
import os
import pprint
pp = pprint.PrettyPrinter(indent=4)


print('\nlocal function call and evaluation with parameter correctly formated as a dict with \'hyperpar\' key and string value.')
par = {'hyperpar': 'x=2\ny=3'}
print(examples.func_def.basic_test_functions.test_griewank(par))


print('\nfunction submission and evaluation on distributed workers with parameter correctly formated as a dict with \'hyperpar\' key and string value:\n')
DASK_MASTER_IP = os.environ['DASK_MASTER_IP']
DASK_MASTER_PORT = os.environ['DASK_MASTER_PORT']
sub_future = []
parameter_string_list = ['x=1\ny=2', 'x=2\ny=4', 'x=3\ny=6']
with Client(DASK_MASTER_IP + ':' + DASK_MASTER_PORT, timeout='20s') as client:
    client.restart()
    pp.pprint(client.scheduler_info())
    client.upload_file(os.path.abspath(examples.func_def.basic_test_functions.__file__))

    # submission of function calls and appending of futures to a list
    # arguments originate from a list of strings and put into a dict one by one
    for s in parameter_string_list:
        parameter = {'hyperpar': s}
        sub_future.append(client.submit(
            examples.func_def.basic_test_functions.test_griewank, parameter))
    for f in as_completed(sub_future):
        # errors occuring during execution of future f inside workers are fetched and reraised with the result() method
        print(f.result())
