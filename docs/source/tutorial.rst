Tutorial
========

This tutorial is intended to give a short introduction on how to use the Modelon Impact Client package to create a workspace, perform a dynamic
simulation on a given model and plot the results.

Initializing the client
-----------------------

Before we set up our workspace and execute our dynamic simulation workflow we need to initialize the
client with the Impact domain. An API key is required to authenticate our login to the server. Refer
to the steps listed in the :doc:`Setup <setup>` section to configure an API key::

   from modelon.impact.client import Client

   client = Client(url=<impact-domain>)

Setting up the workspace
------------------------

Once the client is initialized, we can either create a workspace::

   workspace = client.create_workspace(<workspace-name>)

or upload an existing workspace by specifying the path to the compressed workspace(.zip) to be uploaded::

   workspace = client.upload_workspace(<path_to_workspace>)

This will return an instance of a ``Workspace`` class object with the same name as the zip-file (and
a number appended if another workspace with the same name already exists).

Choosing analysis type
----------------------

Once we have our ``Workspace`` class object, we need to choose an analysis method to fetch the different options available
for configuring our compilation and simulation steps. The analysis methods in Modelon Impact are referred to as custom functions.
There are different analysis methods one can choose from depending on the workflow we intend to use.
We can fetch a list of available analysis methods and print them by executing::

   custom_functions = [
    custom_function.name for custom_function in workspace.get_custom_functions()
   ]
   print(custom_functions)

By default, there are three available custom functions shipped with Impact: ``steady state``, ``dynamic`` and ``linearize``.
It is also possible to create an analysis function for a specific need by following the documentation available in the
Help Center in Modelon Impact (located at <impact url>/help). For this tutorial, we will use the ``dynamic`` custom function::

   dynamic = workspace.get_custom_function('dynamic')

This will return an instance of a ``dynamic`` ``CustomFunction`` class object.

Set up model for analysis
-------------------------

We can either choose a model from a library pre-loaded in Modelon Impact or upload a model to our workspace. To upload
a model to our workspace, we can pass the path to the modelica file::

   model = workspace.upload_model_library('C:/Model.mo')

or choose a model from a pre-loaded library, like ``Modelica Standard Library``::

   model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")

This will return an instance of a ``Model`` class object.

Setting logging levels for analysis
-----------------------------------

The built-in python module, ``logging`` (https://docs.python.org/3.9/library/logging.html) is used by the client. The amount of logging that
should be output by the client can be set by specifying the log level as shown in the code snippet.::

   import logging

   logging.getLogger('modelon.impact.client').setLevel(logging.ERROR)

The log is printed to the standard output, normally the terminal window from which the compiler is invoked. The available log levels are
'INFO'(default), 'ERROR', 'WARNING', 'CRITICAL' and 'DEBUG'.

Analysis
--------

The model analysis can be set up with one of two workflows:

   1. **FMU based workflow**: This workflow requires the user to compile the model to a model executable
   before setting up an experiment for it. This workflow is useful when the user intends to do all the
   computations with the FMUs in a notebook environment(i.e., no experimentation/computation in the Modelon
   Impact server).

   **Note:** Since the user works with the compiled FMUs in the workflow, modifiers added during the
   experimentation step should contain only non-structural parameter modifiers. Any non-structural parameter change
   would require a recompilation of the model.

   2. **Class name based workflow**: This workflow allows the user to directly work with the model class object to setup
   experiments for analysis. The compilation in this workflow is handled as a part of the execution step.
   This workflow allows the users to skip the details of the compilation steps and focus on setting up the experiment
   of interest. Also, this workflow does not impose any restrictions on the parameter modifiers that could be
   applied to the model. If a structural parameter is set as a modifier in a batch run, a recompilation is triggered automatically
   by the client.

1. FMU based workflow
########################

1.1 Compiling the model
***********************

We can compile the model to an FMU for further analysis by calling the ``compile()`` method on the ``model``.
The ``compile()`` method takes one mandatory argument (``compiler_options``) and seven optional ones (``runtime_options``, ``compiler_options``, ``compiler_log_level``,
``fmi_target``, ``fmi_version``, ``platform``, ``force_compilation``).

We can fetch the default values for the mandotory ``compiler_options`` arument and the optional ``runtime_options`` from the
``dynamic`` custom functions.::

   compiler_options = dynamic.get_compiler_options()
   runtime_options = dynamic.get_runtime_options()

To view the default compiler options, the ``dict()`` method can be called on it::

   dict(compiler_options)

It is also possible to apend/modfiy the default options either by calling the ``with_values()`` method on the
``compiler_options`` class object::

   compiler_options_modified = compiler_options.with_values(c_compiler='gcc')

or creating a dictionary of the options::

   compiler_options_modified = {'c_compiler':'gcc'}


With the options now defined, we can pass them to the ``compile()`` method::

   fmu = model.compile(compiler_options=compiler_options_modified,runtime_options=runtime_options).wait()

**Note:**

We have called the ``wait()`` method after the ``compile()`` method to ensure that the compilation process reaches completion.
If ``wait()`` is not called on the model an ``Operation`` object is returned and ``is_completed`` can be used to check the status of the
compilation. Calling the ``wait()`` method returns a ``ModelExecutable`` object which represents the now compiled model.


1.2 Setting up an experiment
****************************

With the ``model`` now compiled as an FMU, we could use it to set up an experiment by defining a ``SimpleFMUExperimentDefinition``
class with our analysis specific parametrization.

This could be done by either creating a ``SimpleFMUExperimentDefinition`` class by passing the fmu and the ``dynamic`` custom
function object::

   from modelon.impact.client import SimpleFMUExperimentDefinition

   experiment_definition = SimpleFMUExperimentDefinition(fmu, dynamic)

or in an even simpler way by calling the ``new_experiment_definition()`` method on the fmu with the ``dynamic`` custom function
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

2. Class name based workflow
############################

2.1 Setting up an experiment
****************************

With the `Class name based workflow`, we could skip the compilation step and setup the experiment
from the model directly.

This could be done by either creating a SimpleModelicaExperimentDefinition class by passing the model
and the dynamic custom function object::

   from modelon.impact.client import SimpleModelicaExperimentDefinition

   experiment_definition = SimpleModelicaExperimentDefinition(model, dynamic)

or in an even simpler way by calling the ``new_experiment_definition()`` method on the model with the ``dynamic`` custom function
object as an argument::

   experiment_definition = model.new_experiment_definition(dynamic)

This would again return a ``SimpleModelicaExperimentDefinition`` class object.

To override the default parameters for the ``dynamic`` simulation workflow, call the ``with_parameters()``
method on the ``dynamic`` custom function class::

   experiment_definition = model.new_experiment_definition(dynamic.with_parameters(start_time=0.0, final_time=2.0))

The default set of parameters available for the custom function can be viewed by calling the property ``parameter_values``::

   dynamic.parameter_values

The ``new_experiment_definition()`` method takes the optional arguments ``solver_options``, ``simulation_options`` and
``simulation_log_level``. If the ``solver_options`` and ``simulation_options`` are not explicitly defined, they default to the ``dynamic``
custom function defaults.

They can be set in a way similar to the compiler_options::

   simulation_options = dynamic.get_simulation_options().with_values(ncp=500)
   solver_options = {'atol':1e-8}
   experiment_definition = model.new_experiment_definition(
       dynamic.with_parameters(start_time=0.0, final_time=2.0),
       solver_options=solver_options,
       simulation_options=simulation_options
   )


Setting up a series of simulations
----------------------------------

Following either of the approaches listed below, the created ``experiment_definition`` can be modified to
set up a series of simulations


Operators
#########
Operators can be used to create multi-execution experiments. Here is an example where a multi-execution
experiment definition with three cases is created::

   from modelon.impact.client import Range

   experiment_definition = experiment_definition.with_modifiers({'PI.k': Range(10, 100, 3)})

Here the ``Range()`` operator class is used to specify the ``start_value``, ``end_value`` and ``no_of_steps`` for the parameter to sweep.
The parametrization in the examples above would configure a set of three simulation cases for the fmu with ``3`` equidistant
values set for the ``PI.k`` parameter, with a start value of ``10`` and an end value of ``100``.

It is also possible to create multi-execution experiments with an explicit list of parameter values to sweep::

   from modelon.impact.client import Choices

   experiment_definition = experiment_definition.with_modifiers({'PI.k': Choices(10, 20, 30, 40)})

Here the ``Choices()`` operator class is used to specify an explicit list of values for the parameter to sweep. The parametrization in the
examples above would configure a set of four simulation cases for the fmu with ``4`` choosen values for the ``PI.k`` parameter.

It also possible to use a combination of the range and choices operators to setup a batch run::

   from modelon.impact.client import Choices

   experiment_definition = experiment_definition.with_modifiers({'PI.k': Choices(10, 20),'PI.Ti.': Range(10, 100, 3)})

Experiment extensions
#####################
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


Executing the experiment
------------------------

The experiment definition set up can now be passed to the ``execute()`` function::

   exp = workspace.execute(experiment_definition).wait()

The ``wait()`` function call here has a similar purpose as the one called on the ``compile()`` function earlier.
Here, the ``Experiment`` class is returned upon completion of the simulation.

Plotting the results
--------------------

With the simulation completed, we can now plot the result trajectories from the batch simulation we setup earlier.
The ``Experiment`` class we got in our previous step has a set of three cases with trajectories for the three different parameter
values we specified for the ``PI.k`` parameter. To fetch the case trajectories for a given experiment the ``get_cases()``
method can be called on the experiment and further it could be checked if the cases did simulate successfully by calling
the ``is_successful()`` method on the case. The ``get_trajectories()`` function can be called on the individual ``case`` objects to
fetch the ``Result`` class object for that specific case.

To plot the results, the variable names of interest could be passed as index variables on the ``Result`` class object::

   import matplotlib.pyplot as plt

   plt.figure(1)
   plt.clf()
   for case in exp.get_cases():
      if case.is_successful():
         result = case.get_trajectories()
         plt.plot(result['time'], result['inertia1.phi'])
   plt.grid()
   plt.show()

If the user wishes to fetch many result variables together, the below workflow could be followed::

   result = exp.get_trajectories(['inertia1.phi', 'time'])
   height_1 = result['case_1']['inertia1.phi']
   time_1 = result['case_1']['time']
   height_2 = result['case_2']['inertia1.phi']
   time_2 = result['case_2']['time']
   height_3 = result['case_3']['inertia1.phi']
   time_3 = result['case_3']['time']
