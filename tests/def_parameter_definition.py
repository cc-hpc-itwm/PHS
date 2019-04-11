def def_parameter_definition(experiment_dir, target_module_root_dir):
    import random as rd
    rd.seed(8856)
    import phs.parameter_definition  # standalone import
    pardef = phs.parameter_definition.ParameterDefinition()

    pardef.set_data_types_and_order([('x', float), ('y', float)])

    pardef.add_individual_parameter_set(
        set={'x': {'type': 'explicit', 'value': 0.5},
             'y': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 1}})

    pardef.add_individual_parameter_set(
        number_of_sets=20,
        set={'x': {'type': 'random', 'bounds': [-5, 5], 'distribution': 'uniform', 'round_digits': 3},
             'y': {'type': 'random_from_list', 'lst': [1.2, 3.4, 5.4, 6.3]}},
        prevent_duplicate=True)

    pardef.export_parameter_definitions(export_path=experiment_dir)

    rd.seed()
