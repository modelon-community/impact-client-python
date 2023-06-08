FMU based workflow 
==================

*This tutorial covers setting up an experiment with the FMU based workflow.*

This workflow requires the user to compile the model to a model executable
before setting up an experiment for it. This workflow is useful when the user intends to do all the
computations with the FMUs in a notebook environment(i.e., no experimentation/computation in the Modelon
Impact server).

**Note:** Since the user works with the compiled FMUs in the workflow, modifiers added during the
experimentation step should contain only non-structural parameter modifiers. Any non-structural parameter change
would require a recompilation of the model.

Workflow
########

1.1 Compiling the model
***********************

The model can be compiled to an FMU for further analysis by calling the ``compile()`` method on the ``model``.
The ``compile()`` method takes one mandatory argument (``compiler_options``) and seven optional ones (``runtime_options``, ``compiler_options``, ``compiler_log_level``,
``fmi_target``, ``fmi_version``, ``platform``, ``force_compilation``).

We can fetch the default values for the mandatory ``compiler_options`` argument and the optional ``runtime_options`` from the
``dynamic`` custom functions.::

   compiler_options = dynamic.get_compiler_options()
   runtime_options = dynamic.get_runtime_options()

To view the default compiler options, the ``dict()`` method can be called on it::

   dict(compiler_options)

It is also possible to append/modify the default options either by calling the ``with_values()`` method on the
``compiler_options`` class object::

   compiler_options_modified = compiler_options.with_values(c_compiler='gcc')

or creating a dictionary of the options::

   compiler_options_modified = {'c_compiler':'gcc'}


With the options now defined, we can pass them to the ``compile()`` method::

   fmu = model.compile(compiler_options=compiler_options_modified,runtime_options=runtime_options).wait()

**Note:**

We have called the ``wait()`` method after the ``compile()`` method to ensure that the compilation process reaches completion.
If ``wait()`` is not called on the model an ``Operation`` object is returned and ``is_complete()`` can be used to check the status of the
compilation. Calling the ``wait()`` method returns a ``ModelExecutable`` object which represents the now compiled model.


1.2 Setting up an experiment
****************************

With the ``model`` now compiled as an FMU, we could use it to set up an experiment by defining a ``SimpleFMUExperimentDefinition``
class with our analysis specific parametrization.

This could be done by either creating a ``SimpleFMUExperimentDefinition`` class by passing the FMU and the ``dynamic`` custom
function object::

   from modelon.impact.client import SimpleFMUExperimentDefinition

   experiment_definition = SimpleFMUExperimentDefinition(fmu, dynamic)

or in an even simpler way by calling the ``new_experiment_definition()`` method on the FMU with the ``dynamic`` custom function
object as an argument::

   experiment_definition = fmu.new_experiment_definition(dynamic)

This would again return a ``SimpleFMUExperimentDefinition`` class object.

To override the default parameters for the ``dynamic`` simulation workflow, call the ``with_parameters()``
method on the ``dynamic`` custom function class::

   experiment_definition = fmu.new_experiment_definition(dynamic.with_parameters(start_time=0.0, final_time=2.0))

The default set of parameters available for the custom function can be viewed by calling the property ``parameter_values``::

   dynamic.parameter_values

The ``new_experiment_definition()`` method takes the optional arguments ``solver_options``, ``simulation_options`` and
``simulation_log_level``. If the ``solver_options`` and ``simulation_options`` are not explicitly defined, they default to the ``dynamic``
custom function defaults.

They can be set in a way similar to the compiler_options::

   solver_options = {'atol':1e-8}
   simulation_options = dynamic.get_simulation_options().with_values(ncp=500)
   experiment_definition = fmu.new_experiment_definition(dynamic.with_parameters(start_time=0.0, final_time=2.0),
   solver_options, simulation_options)
