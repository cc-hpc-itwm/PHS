import phs.parameter_definition  # standalone import

pardef = phs.parameter_definition.ParameterDefinition()

pardef.set_data_types_and_order([('x', float), ('y', float)])

pardef.add_individual_parameter_set(
    number_of_sets=15,
    set={'x': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 3},
         'y': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 3}},
    prevent_duplicate=True)

pardef.add_individual_parameter_set(
    number_of_sets=5,
    set={'x': {'type': 'bayesian', 'bounds': [-4, 3], 'round_digits': 3},
         'y': {'type': 'bayesian', 'bounds': [-5, 6], 'round_digits': 3}})

pardef.export_parameter_definitions(export_path='absolute/path/to/parent/folder/for/export')
