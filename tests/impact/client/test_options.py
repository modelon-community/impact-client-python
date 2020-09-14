from tests.impact.client.fixtures import *


def test_modify_options(
    compiler_options, runtime_options, solver_options, simulation_options
):

    simulation_opts = simulation_options.with_values(ncp=10)
    runtime_opts = runtime_options.with_values(log_level=1)
    solver_opts = solver_options.with_values(rtol=50)
    compiler_opts = compiler_options.with_values(c_compiler=4)

    assert compiler_opts.to_dict() == {'c_compiler': 4}
    assert runtime_opts.to_dict() == {'log_level': 1}
    assert simulation_opts.to_dict() == {'ncp': 10}
    assert solver_opts.to_dict() == {'rtol': 50}


def test_append_options(
    compiler_options, runtime_options, solver_options, simulation_options
):

    simulation_opts = simulation_options.with_values(a=10)
    runtime_opts = runtime_options.with_values(b="hello")
    solver_opts = solver_options.with_values(c=5.0)
    compiler_opts = compiler_options.with_values(d=True)

    assert compiler_opts.to_dict() == {'c_compiler': 'gcc', 'd': True}
    assert runtime_opts.to_dict() == {'log_level': 3, 'b': 'hello'}
    assert simulation_opts.to_dict() == {'ncp': 2000, 'a': 10}
    assert solver_opts.to_dict() == {'rtol': 0.0001, 'c': 5.0}
