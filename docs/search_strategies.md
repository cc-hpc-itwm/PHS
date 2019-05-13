# Search Strategies

At this time the following three search strategies are available.

+ explicit
+ random
+ bayesian optimization

You do not have to decide for one option. Instead its possible to mix them up in terms of different parameters and even for the parameter sets. Independent from your choice the setup of the search strategy is all about creating a table where each column represents a different parameter and each row represents a parameter set. Each set forms a unit for the input argument of one function evaluation.

First you have to name all your parameters. Be careful to use names expected by your target function. Referring to the ```test_griewank``` ```x``` and ```y```are needed unless you rename them inside your target function.

## How to setup the Parameters

A seperate class takes care of the parameter setup which is needed for subsequent experiments. In general three steps have to be done.

+ set the parameter data types and order via a list of tuples (see [Data Types, Order and Transfer of parameters](data_types_order_transfer.md) for detailed explanations)

```python
import phs.parameter_definition
pardef = phs.parameter_definition.ParameterDefinition()

pardef.set_data_types_and_order([('x', float), ('y', float)])
```

+ chose one or a combination of multiple search strategies

```python
pardef.add_individual_parameter_set(
    set={'x': {'type': 'explicit', 'value': 0.5},
         'y': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 1}})

pardef.add_individual_parameter_set(
    number_of_sets=5,
    set={'x': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 3},
         'y': {'type': 'random_from_list', 'lst': [1.2, 3.4, 5.4, 6.3]}},
    prevent_duplicate=True)

inst.add_individual_parameter_set(
    number_of_sets=10,
    set={'x': {'type': 'bayesian', 'bounds': [-5, 5], 'round_digits': 3},
         'y': {'type': 'bayesian', 'bounds': [-5, 5], 'round_digits': 3}})
```

+ export the definitions for later usage

```python
pardef.export_parameter_definitions(
    export_path='absolute/path/to/parent/folder/for/export')
```
+ or directly feed them into an experiment definition

```python
import phs.experiment_definition

expdef = phs.experiment_definition.ExperimentDefinition(
    ...
    parameter_definitions=pardef.get_parameter_definitions())
```

## Detailed Explanation

With the method ```add_individual_parameter_set``` you can define one or multiple parameter sets with a search strategy for each parameter.

```python
add_individual_parameter_set(number_of_sets=1, set={}, prevent_duplicate=True)
```

With ```number_of_sets``` you can generate multiple sets with the given options. If ```prevent_duplicate``` is ```True``` identical sets are recognized and redrawn again. This option only makes sense if at least one parameter is set randomly.


```set``` expects a nested dictionary. The outer keywords correspond to the parameter names. The corresponding values form the inner dictionaries which define the search strategies. You have the following options for the value of the keyword ```'type'```.

### ```'explicit'```
Here is not much to say. The given value is assigned to the parameter, what can be useful when some initial guesses should be evaluated.

```python
{'type': 'explicit', 'value': 0.5}
```


### ```'random'```
A value is drawn from the ```'distribution'``` between the ```'bounds':[low, high]```. Optionally you can round the value to ```'round_digits'```.

```python
{'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 1}
```

### ```'random_from_list'```
Randomly draw one element from the list ```'lst'```.

```python
{'type': 'random_from_list', 'lst': [1.2, 3.4, 5.4, 6.3]}
```

### ```'bayesian'```
No value will be set yet. Instead a placeholder is assigned to mark it as a bayesian task. A parameter set containing any bayesian placeholder is scheduled as normal. When it comes to executing all previously finished evaluations (parameter sets + results) are loaded by the worker. With these information the bayesian optimization algorithm is started to suggest values inside the ```'bounds':[low, high]``` for all the parameters holding a bayesian placeholder. Optionally you can round the value to ```'round_digits'```.

```python
{'type': 'bayesian', 'bounds': [-5, 5], 'round_digits': 3}
```

## Example

```python
pardef.add_individual_parameter_set(
    set={'x': {'type': 'explicit', 'value': 2.5},
         'y': {'type': 'explicit', 'value': -3.12}})

pardef.add_individual_parameter_set(
    number_of_sets=3,
    set={'x': {'type': 'random', 'bounds': [-2, 2], 'distribution': 'uniform', 'round_digits': 2},
         'y': {'type': 'random_from_list', 'lst': [1.23, 3.4, 5.4, 6.3]}},
    prevent_duplicate=True)

inst.add_individual_parameter_set(
    number_of_sets=2,
    set={'x': {'type': 'bayesian', 'bounds': [-5, 5], 'round_digits': 3},
         'y': {'type': 'random', 'bounds': [-10, 2], 'distribution': 'uniform', 'round_digits': 3}})
```


|    | x       | y      |
|----|---------|--------|
|0   |   2.500 | -3.120 |
|1   |   1.420 |  5.400 |
|2   |  -1.870 |  6.300 |
|3   |   1.550 |  1.230 |
|4   |   0.000 | -6.561 |
|5   |   0.000 |  0.785 |
