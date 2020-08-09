import pytest
from tests.impact.client.fixtures import *


def test_options(options):
    assert options.to_dict() == {
        'compiler': {'c_compiler': 'gcc'},
        'runtime': {'log_level': 3},
        'simulation': {'ncp': 2000},
        'solver': {'rtol': 0.0001},
    }
    options.simulation(ncp=10)
    options.runtime(log_level=1)
    options.solver(rtol=50)
    options.compiler(c_compiler=4)
    assert options.to_dict() == {
        'compiler': {'c_compiler': 4},
        'runtime': {'log_level': 1},
        'simulation': {'ncp': 10},
        'solver': {'rtol': 50},
    }
    options.reset()
    assert options.to_dict() == {
        'compiler': {'c_compiler': 'msvs'},
        'runtime': {'log_level': 2},
        'simulation': {'ncp': 500},
        'solver': {'rtol': 1e-05},
    }
    assert options.defaults == {
        'compiler': {'c_compiler': 'msvs'},
        'runtime': {'log_level': 2},
        'simulation': {'ncp': 500},
        'solver': {'rtol': 1e-05},
    }


def test_simulation_options(options):
    options.simulation(a=1)
    assert options.to_dict()["simulation"] == {'a': 1, 'ncp': 2000}
    assert options.simulation().values == {'a': 1, 'ncp': 2000}
    options.simulation().reset()
    assert options.simulation().values == {'ncp': 500}
    assert options.simulation().defaults == {'ncp': 500}


def test_change_existing_simulation_options(options):
    options.simulation(ncp=1)
    assert options.to_dict()["simulation"] == {'ncp': 1}
    assert options.simulation().values == {'ncp': 1}


def test_runtime_options(options):
    options.runtime(ab=1)
    assert options.to_dict()["runtime"] == {'ab': 1, 'log_level': 3}
    assert options.runtime().values == {'ab': 1, 'log_level': 3}
    options.runtime().reset()
    assert options.runtime().values == {'log_level': 2}
    assert options.runtime().defaults == {'log_level': 2}


def test_change_existing_runtime_options(options):
    options.runtime(log_level=1)
    assert options.to_dict()["runtime"] == {'log_level': 1}
    assert options.runtime().values == {'log_level': 1}


def test_compiler_options(options):
    options.compiler(ac=1)
    assert options.to_dict()["compiler"] == {'ac': 1, 'c_compiler': 'gcc'}
    assert options.compiler().values == {'ac': 1, 'c_compiler': 'gcc'}
    options.compiler().reset()
    assert options.compiler().values == {'c_compiler': 'msvs'}
    assert options.compiler().defaults == {'c_compiler': 'msvs'}


def test_change_existing_compiler_options(options):
    options.compiler(c_compiler=1)
    assert options.to_dict()["compiler"] == {'c_compiler': 1}
    assert options.compiler().values == {'c_compiler': 1}


def test_solver_options(options):
    options.solver(ad=1)
    assert options.to_dict()["solver"] == {'ad': 1, 'rtol': 0.0001}
    assert options.solver().values == {'ad': 1, 'rtol': 0.0001}
    options.solver().reset()
    assert options.solver().values == {'rtol': 1e-5}
    assert options.solver().defaults == {'rtol': 1e-5}


def test_change_existing_solver_options(options):
    options.solver(rtol=1)
    assert options.to_dict()["solver"] == {'rtol': 1}
    assert options.solver().values == {'rtol': 1}


def test_delete_option_not_exist(options):
    pytest.raises(KeyError, options.delete, 'solver', 'lol')
