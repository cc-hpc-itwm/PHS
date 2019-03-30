import phs.functional_test_processes


def test_functional_test_processes():
    assert sorted(phs.functional_test_processes.functional_test_processes()) == sorted([8, 2, 18])
