from concurrent.futures import ProcessPoolExecutor, as_completed


def task(hyperpar):
    # pylint: disable=E0602
    exec(hyperpar, globals(), globals())
    result = x * y
    return result


def functional_test_processes():
    sub_future = []
    return_list = []
    parameter_string_list = ['x=1\ny=2', 'x=2\ny=4', 'x=3\ny=6']
    with ProcessPoolExecutor(max_workers=2) as executor:
        for s in parameter_string_list:
            sub_future.append(executor.submit(task, s))
        for f in as_completed(sub_future):
            # errors occuring during execution of future f inside workers are fetched
            # and reraised with the result() method
            return_list.append(f.result())
    return return_list


def main():
    print(functional_test_processes())
    return 0


if __name__ == '__main__':
    main()
