import pytest


def test_modify_options(
    compiler_options, runtime_options, solver_options, simulation_options
):

    simulation_opts = simulation_options.with_values(ncp=10)
    runtime_opts = runtime_options.with_values(log_level=1)
    solver_opts = solver_options.with_values(rtol=50)
    compiler_opts = compiler_options.with_values(c_compiler=4)

    assert dict(compiler_opts) == {"c_compiler": 4}
    assert dict(runtime_opts) == {"log_level": 1}
    assert dict(simulation_opts) == {"ncp": 10}
    assert dict(solver_opts) == {"rtol": 50}


def test_append_options(
    compiler_options, runtime_options, solver_options, simulation_options
):

    simulation_opts = simulation_options.with_values(a=10)
    runtime_opts = runtime_options.with_values(b="hello")
    solver_opts = solver_options.with_values(c=5.0)
    compiler_opts = compiler_options.with_values(d=True)

    assert dict(compiler_opts) == {"c_compiler": "gcc", "d": True}
    assert dict(runtime_opts) == {"log_level": 3, "b": "hello"}
    assert dict(simulation_opts) == {"ncp": 2000, "a": 10}
    assert dict(solver_opts) == {"rtol": 0.0001, "c": 5.0}


def test_simulation_options_with_result_filter(simulation_options):

    simulation_opts = simulation_options.with_result_filter(filter=["*.phi"])

    assert dict(simulation_opts) == {"filter": "['*.phi']", "ncp": 2000}


def test_simulation_options_with_result_filter_invalid_string_imput(simulation_options):
    with pytest.raises(ValueError):
        simulation_options.with_result_filter(filter="*.phi")


def test_simulation_options_with_result_filter_invalid_list_imput(simulation_options):
    with pytest.raises(ValueError):
        simulation_options.with_result_filter(filter=["*.phi", 2])
