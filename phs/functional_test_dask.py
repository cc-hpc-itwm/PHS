import examples.func_def.test_functions
# import carme
from dask.distributed import Client, as_completed
import os
import pprint
pp = pprint.PrettyPrinter(indent=4)
# carme.resetKernel()
# carme.addCarmePythonPath('/home/HabelitzP/parallel_hyperparameter_search/examples')
# carme.resetKernel()
# import CarmeModules.HyperParameterSearch.examples.test_functions as test_functions
# repository_root_dir = '/home/HabelitzP' #(example:'/home/NAME')
# import sys
# sys.path.append(repository_root_dir + '/parallel_hyperparameter_search/examples')

'''def task(hyperpar):
    exec(hyperpar, globals(), globals())
    result = x * y
    return result'''
par = {'hyperpar': 'x=2\ny=3'}
print(examples.func_def.test_functions.test_griewank(par))
DASK_MASTER_IP = os.environ['DASK_MASTER_IP']
DASK_MASTER_PORT = os.environ['DASK_MASTER_PORT']
sub_future = []
parameter_string_list = ['x=1\ny=2', 'x=2\ny=4', 'x=3\ny=6']
with Client(DASK_MASTER_IP + ':' + DASK_MASTER_PORT, timeout='20s') as client:
    pp.pprint(client.scheduler_info())
    client.upload_file(
        '/home/HabelitzP/parallel_hyperparameter_search/examples/func_def/basic_test_functions.py')
    for s in parameter_string_list:
        parameter = {'hyperpar': s}
        sub_future.append(client.submit(
            examples.func_def.basic_test_functions.test_griewank, parameter))
    for f in as_completed(sub_future):
        # errors occuring during execution of future f inside workers are fetched and reraised with the result() method
        print(f.result())
