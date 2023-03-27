Multi-execution experiments
===========================

*This tutorial covers different ways to setup a series of simulations.*


Following either of the approaches listed below, the experiment definition can be modified to
set up a series of simulations

Operators
---------

Operators can be used to create multi-execution experiments. Here is an example 
where an experiment definition (see :ref:`Setting up an experiment <Setting up an experiment>` 
section for base setup of experiments) is augmented to execute multiple cases::

   from modelon.impact.client import Range

   experiment_definition = experiment_definition.with_modifiers({'PI.k': Range(10, 100, 3)})

Here the ``Range()`` operator class is used to specify the ``start_value``, ``end_value`` and ``no_of_steps`` for the parameter to sweep.
The parametrization in the examples above would configure a set of three simulation cases for the model with ``3`` equidistant
values set for the ``PI.k`` parameter, with a start value of ``10`` and an end value of ``100``.

It is also possible to create multi-execution experiments with an explicit list of parameter values to sweep::

   from modelon.impact.client import Choices

   experiment_definition = experiment_definition.with_modifiers({'PI.k': Choices(10, 20, 30, 40)})

Here the ``Choices()`` operator class is used to specify an explicit list of values for the parameter to sweep. The parametrization in the
examples above would configure a set of four simulation cases for the FMU with ``4`` chosen values for the ``PI.k`` parameter.

It also possible to use a combination of the range and choices operators to setup a batch run::

   from modelon.impact.client import Choices

   experiment_definition = experiment_definition.with_modifiers({'PI.k': Choices(10, 20),'PI.Ti.': Range(10, 100, 3)})

Experiment extensions
---------------------

The experiment extensions approach provides a more flexible and highly parametrizable way to create a multi-execution scenario.
The extensions could be defined by calling the ``with_extensions()`` method on the ``experiment_definition``
class object with a list of ``SimpleExperimentExtension()`` classes as input. The ``SimpleExperimentExtension()`` could be parametrized
with inputs such as the ``custom_function parameters``, ``solver_options``, ``simulation_options`` and ``simulation_log_level``::

   from modelon.impact.client import SimpleExperimentExtension

   experiment_extension_1 = SimpleExperimentExtension(
      parameter_modifiers={'final_time': 2.0},
      solver_options={'atol': 1e-9},
      simulation_options=dynamic.get_simulation_options().with_values(ncp=1500),
   )
   experiment_extension_2 = SimpleExperimentExtension(
      parameter_modifiers={'final_time': 5.0},
      solver_options={'atol': 1e-10},
      simulation_options=dynamic.get_simulation_options().with_values(ncp=1200),
   )

This would create two simulation cases with different solver and simulation settings. It is also possible to have different
variable modifiers for each of these cases. This could be done by calling the ``with_modifiers()`` method on the
``SimpleExperimentExtension()`` class::

   experiment_extension_1 = experiment_extension_1.with_modifiers({'PI.k': 25})
   experiment_extension_2 = experiment_extension_2.with_modifiers({'PI.Ti': 5})

The extensions could be passed on as a list of arguments to the ``with_extensions()`` method on the ``experiment_definition``
class object::

   experiment_definition = experiment_definition.with_extensions(
      [experiment_extension_1, experiment_extension_2]
   )

A simpler approach for parametrization also exists for scenarios where only variable modifiers are varied for setting up
multi-execution cases. This could be done by calling the ``with_cases()`` method on the ``experiment_definition`` class object
with the variable modifiers as inputs::

   experiment_definition = experiment_definition.with_cases([{'PI.k': 20}, {'PI.k': 30}])

**Note:**

It is not supported to have both range operator and experiment extensions defined for an experiment. The simulation cases
could only be set up with one of the two methods. However, it is allowed to call the  ``with_modifiers`` method on the
``experiment_definition`` class to specify variables to modify. The modified variable in such a scenario would be set in all
the cases defined using the ``with_extensions()`` or ``with_cases()`` method calls. If the same variable modifier is
set in both ``experiment_definition`` and extensions, the one set in the extensions would gain precedence, overriding the former.


