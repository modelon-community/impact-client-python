from tests.impact.client.fixtures import *


def test_modify_options(options):
    assert options.to_dict() == {
        'compiler': {'c_compiler': 'gcc'},
        'runtime': {'log_level': 3},
        'simulation': {'ncp': 2000},
        'solver': {'rtol': 0.0001},
    }
    new_opts = (
        options.with_simulation_options(ncp=10)
        .with_runtime_options(log_level=1)
        .with_solver_options(rtol=50)
        .with_compiler_options(c_compiler=4)
    )
    assert new_opts.to_dict() == {
        'compiler': {'c_compiler': 4},
        'runtime': {'log_level': 1},
        'simulation': {'ncp': 10},
        'solver': {'rtol': 50},
    }


def test_append_options(options):
    assert options.to_dict() == {
        'compiler': {'c_compiler': 'gcc'},
        'runtime': {'log_level': 3},
        'simulation': {'ncp': 2000},
        'solver': {'rtol': 0.0001},
    }
    new_opts = (
        options.with_simulation_options(a=10)
        .with_runtime_options(b="hello")
        .with_solver_options(c=5.0)
        .with_compiler_options(d=True)
    )
    assert new_opts.to_dict() == {
        'compiler': {'c_compiler': 'gcc', 'd': True},
        'runtime': {'log_level': 3, 'b': 'hello'},
        'simulation': {'ncp': 2000, 'a': 10},
        'solver': {'rtol': 0.0001, 'c': 5.0},
    }
