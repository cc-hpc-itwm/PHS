# Parameter Data Types
All numpy dtypes and in addition the special flag ```'expr'``` can be used as data types for your parameters.

### Python Expression
If a parameter should contain an expression such as ```math.sin(x)``` there is a problem. Such an expression will be evaluated immediately what is not intended. To prevent this you have to use quotes to mask such statements as a string. Furthermore the data type ```'expr'``` indicates that the respective parameter has to be interpreted as a python expression and not as a string.

### String
A parameter can also contain a real string. Just declare the respective parameter data type as a ```str``` and mask the values with quotes.


## Order of Parameters
The order of the parameters can come into play if a parameter is from data type ```expr``` and contains a variable which is also set in the parameter definition. So the order in which the data types are defined is crucial. When setting the search strategies of the parameters the order is irrelevant.


Consider an application where you want to evaluate different mathematical functions ```f_x``` with random inputs ```x```. Because the input has to be defined before evaluation of ```f_x``` can happen the order of your parameters must be:

```python
import phs.parameter_definition  # standalone import

pardef = phs.parameter_definition.ParameterDefinition()

pardef.set_data_types_and_order([('x', float), ('f_x', 'expr')])
```

The definition of your parameters then could look like:

```Python
pardef.add_individual_parameter_set(
    number_of_sets=3,
    set={'f_x': {'type': 'random_from_list', 'lst': ['math.sin(x)', 'math.cos(x)', 'math.tan(x)']},
         'x': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 3}},
    prevent_duplicate=True)
```

# Parameter Transfer
A detail which helps to understand how the generality of this framework is achieved concern the transfer of parameters from the definition down to the target function.

After the setup each parameter set is packed into a single string, passed as an argument to the target function and executed there in place utilizing the python method ```exec()```. This results in a behavior like hard coded definitions and enables to leave the modifications inside the target functions static and independent.

## Demonstration of the Transfer

The following full example shows how the transfer works. Beside the usage of different data types, especially ```expr``` and the order become clearer.

```python
def main():
    import phs.parameter_definition  # standalone import
    import phs.experiment_definition  # standalone import
    import phs.compute_definition  # standalone import

    pardef = phs.parameter_definition.ParameterDefinition()

    pardef.set_data_types_and_order([('x', float), ('f', 'expr'), ('iterations', int), ('s', str)])

    pardef.add_individual_parameter_set(
        number_of_sets=3,
        set={'x': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 3},
             'f': {'type': 'random_from_list', 'lst': ['math.sin(x)', 'math.cos(x)', 'math.tan(x)']},
             'iterations': {'type': 'random', 'bounds': [1, 7], 'distribution': 'uniform', 'round_digits': 0},
             's': {'type': 'random_from_list', 'lst': ['string1', 'string2', 'string3']}},
        prevent_duplicate=True)

    expdef = phs.experiment_definition.ExperimentDefinition(
        experiment_dir='/absolute/path/to/not/yet/existing/folder/your/experiments/should/be/saved',
        target_module_root_dir='/absolute/path/to/root/dir/in/which/your/test_function/resides',
        target_module_name='file_name_with_test_function_definition_(without_extension)',
        target_function_name='data_types_and_order_func',
        parameter_definitions=pardef.get_parameter_definitions())

    compdef = phs.compute_definition.ComputeDefinition(
        experiment_dir='/absolute/path/to/folder/with/existing/experiment',
        parallelization='local_processes',
        local_processes_num_workers=1,
        redirect_stdout=True)

    compdef.start_execution()


if __name__ == "__main__":
    main()

```

A simple toy target function expects the defined parameters and prints them into the redirected stdout (see [Experiment Definition](experiment_definition.md) for more information about redirecting).

```python
import math

def data_types_and_order_func(parameter):
    exec(parameter['hyperpar'], globals(), globals())
    print(parameter['hyperpar'])
    string_list = []
    for i in range(iterations):
        string_list.append(s)
    return f
```

These three parameter sets packed into a single string each:

```python
'x=2.564\nf=math.tan(x)\niterations=3\ns="string2"'
'x=1.335\nf=math.sin(x)\niterations=7\ns="string2"'
'x=-4.509\nf=math.cos(x)\niterations=1\ns="string3"'
```


Each string is transferred inside the dictionary entry ```parameter['hyperpar']``` to the target function, where it is executed. This corresponds to following functions with hard coded definitions:

```python
import math

def data_types_and_order_func(parameter):
    x=2.564
    f=math.tan(x)
    iterations=3
    s="string2"
    print(parameter['hyperpar'])
    string_list = []
    for i in range(iterations):
        string_list.append(s)
    return f
```

```python
import math

def data_types_and_order_func(parameter):
    x=1.335
    f=math.sin(x)
    iterations=7
    s="string2"
    print(parameter['hyperpar'])
    string_list = []
    for i in range(iterations):
        string_list.append(s)
    return f
```

```python
import math

def data_types_and_order_func(parameter):
    x=-4.509
    f=math.cos(x)
    iterations=1
    s="string3"
    print(parameter['hyperpar'])
    string_list = []
    for i in range(iterations):
        string_list.append(s)
    return f
```
