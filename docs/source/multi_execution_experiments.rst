Multi-execution experiments
===========================

*This tutorial covers different ways to setup a series of simulations.*

Multi-execution experiments include a set of simulation cases with different
parametrization that can be executed in parallel. All cases in a multi-execution
experiment refer to the same model but may be structurally
different if structural model parameters are changed between the cases.
The multi-execution framework automatically determines if several model
compilations are required for the execution.

Multi-execution experiments can be setup either:

1. declaratively via :ref:`expansions <Experiment expansions>`. This involves using
a set of predefined operators along with corresponding expansion algorithms to generate the cases.

2. explicitly by defining individual cases via :ref:`definition extensions<Experiment extensions>`.

Following either of the approaches, the experiment definition can be modified to
set up a series of simulations

Experiment expansions
^^^^^^^^^^^^^^^^^^^^^

Operators
---------

Operators can be used to create multi-execution experiments. There are multiple operator types available:

   1. :class:`Choices<.modelon.impact.client.experiment_definition.operators.Choices>`
   2. :class:`Range<.modelon.impact.client.experiment_definition.operators.Range>`
   3. Distributions - The following distributions are supported:-

      a. :class:`Uniform<.modelon.impact.client.experiment_definition.operators.Uniform>`
      b. :class:`Normal<.modelon.impact.client.experiment_definition.operators.Normal>`
      c. :class:`Beta<.modelon.impact.client.experiment_definition.operators.Beta>`
      
Here is an example where an experiment definition (see :ref:`Setting up an experiment <Setting up an experiment>` 
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

   experiment_definition = experiment_definition.with_modifiers({'PI.k': Choices(10, 20),'PI.Ti': Range(10, 100, 3)})

Expansion types
---------------

The operators could be further customized with expansion algorithms. Expansion methods define 
how cases of an experiment are selected based on the respective operators. The following expansion
algorithms are supported:

1. :class:`Full-factorial<.modelon.impact.client.experiment_definition.expansion.FullFactorial>`: Creates 
an experiment with all possible combinations of the respective operators. Supported operators are Range and Choices.
Note: Full-factorial is the default and does not need to be specified explicitly. Example::

   from modelon.impact.client import Range, Choices

   experiment_definition = experiment_definition.with_modifiers({'PI.k': Choices(10, 20),'PI.Ti': Range(10, 100, 3)})

2. :class:`Latin-hypercube<.modelon.impact.client.experiment_definition.expansion.LatinHypercube>`: Supported
operators are Uniform, Normal and Beta. The values for the resulting cases are produced as follows:

   a. Each operator expression is subdivided into samples partitions of equal probability. E.g., 
      given samples = 10, Uniform(0, 10) is subdivided into [0, 1), [1, 2), … , [9, 10). For each case, a random, 
      but distinct, subdivision is chosen and a random (in accordance with the given probability distribution) 
      value is chosen for the given Case.
   b. The resulting cases are called orthogonal. Values corresponding to a given operator expression do not 
      repeat among all cases of an Experiment.

Example::

   from modelon.impact.client import Beta, Normal, LatinHypercube

   experiment_definition = model.new_experiment_definition(
         custom_function).with_modifiers({'inertia1.J': Beta(0.1, 0.9),
         'inertia2.J': Normal(0.1, 0.5)}).with_expansion(LatinHypercube(5,0))

3. :class:`Sobol<.modelon.impact.client.experiment_definition.expansion.Sobol>`: The expansion produces samples
cases, based on the Sobol sequence. Supported operators are Uniform, Normal and Beta. An example with `Uniform`
operator with `Sobol` expansion algorithm can be found :ref:`here<Sobol space coverage>`. Example::

   from modelon.impact.client import Beta, Normal, Sobol

   experiment_definition = model.new_experiment_definition(
         custom_function).with_modifiers({'inertia1.J': Beta(0.1, 0.9),
         'inertia2.J': Normal(0.1, 0.5)}).with_expansion(Sobol(5))

Experiment extensions
^^^^^^^^^^^^^^^^^^^^^

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


