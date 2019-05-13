# parameter_definition

## ParameterDefinition
```python
ParameterDefinition(self)
```

### set_data_types_and_order
```python
ParameterDefinition.set_data_types_and_order(self, parameter_data_types_and_order)
```

Set the data types and order of the parameters which should be used in the framework.

Parameters
----------
- **parameter_data_types_and_order** (list): list of tuples, each consists of parameter name and data type.
order of tuples represents order of parameters.

    - example:
    ```python
    [('x', float), ('y', float)]
    ```

### set_data_types_and_order_listed
```python
ParameterDefinition.set_data_types_and_order_listed(self, parameter_list, datatype_list=[], datatype_for_all=None)
```

An alternative to set the data types and order via a simple list. The data types can be set with a second list
or via a single type for all.

Parameters
----------
- **parameter_list** (list): parameter names to represent their order
- **datatype_list** (list, Default value = []): datatype for each parameter
- **datatype_for_all** (datatype, Default value = None): data type applied to all parameters

### add_individual_parameter_set
```python
ParameterDefinition.add_individual_parameter_set(self, number_of_sets=1, set={}, prevent_duplicate=True)
```

Add one or multiple parameter sets to your parameter definition.

Parameters
----------
- **number_of_sets** (int, Default value = 1): number of parameter sets to be generated
- **set** (dict, Default value = {}): two nested dicts defining the generation of a parameter set. the outer
dict keywords represent the parameter names while the respective values are the inner dicts defining how this
parameter should be generated (see documentation for more information).
- **prevent_duplicate** (Default value = True): If True, each generated parameter set is checked for
equality against all parameter sets already included in the parameter definition. In case an identity is found,
the current parameter set is redrawn again. If there is any bayesian task in the set, the check is skipped.
    - example:

        ```python
        add_individual_parameter_set(
            number_of_sets=20,
            set={'x': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 3},
                 'y': {'type': 'random_from_list', 'lst': [1.2, 3.4, 5.4, 6.3]}},
                 prevent_duplicate=True)
        ```

### add_listed_parameter_set
```python
ParameterDefinition.add_listed_parameter_set(self, number_of_sets, parameter_list, options, prevent_duplicate=True)
```

An alternative to define parameter sets via a list.

Parameters
----------
- **number_of_sets** (int): number of parameter sets to be generated
- **parameter_list** (list): a list containing all parameter names
- **options** (dict): options are applied to all parameters. the mandatory keyword which has to be filled with
a value is ```'type_for_all'```. There are four types available. Depending on the choice the some other
keywords become compulsary.
    - ```'random'```

        -> ```'bounds_for_all'``` (list): borders of the random draw [low, high]

        -> ```'round_digits_for_all'``` (int): round value to given number of digits

    - ```'random_from_list'```

        -> ```'lst_for_all'``` (list): list from which one element is randomly picked

    - ```'explicit'```

        -> ```'value_for_all'``` (): value provided here is assigned to all parameters

    - ```'bayesian'```

        -> ```'bounds_for_all'``` (list): borders of the bayesian optimization [low, high]

- **prevent_duplicate** (Default value = True): If True, each generated parameter set is checked for
equality against all parameter sets already included in the parameter definition. In case an identity is found,
the current parameter set is redrawn again. If there is any bayesian task in the set, the check is skipped.
    - example:

        ```python
        add_listed_parameter_set(
            number_of_sets=10,
            parameter_list=['x1', 'x2', 'x3'],
            options={'type_for_all': 'random', 'bounds_for_all': [1, 34], 'round_digits_for_all': 2},
            prevent_duplicate=True)
        ```

### register_parameter_set
```python
ParameterDefinition.register_parameter_set(self)
```

### finalize_parameter_definitions
```python
ParameterDefinition.finalize_parameter_definitions(self)
```

### export_parameter_definitions
```python
ParameterDefinition.export_parameter_definitions(self, export_path)
```

Save the complete parameter definition of the class instance to hard disc. It contains several human readable
files and meet the requirements to be reused in the parallel_hyperparameter_search class.

Parameters
----------
- **export_path** (string): absolute path to a parent folder in which the parameter definitions are saved

### get_parameter_definitions
```python
ParameterDefinition.get_parameter_definitions(self)
```
