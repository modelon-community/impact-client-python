Setup and run an experiment
===========================

*This tutorial sections covers setting up an experiment and executing it.* 

This tutorial will use the setup of workspace, model, and analysis as::

  workspace = client.create_workspace(<workspace name>)
  model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")
  dynamic = workspace.get_custom_function('dynamic')

See previous tutorial chapters for details.

Setting up an experiment
************************

The experiment can be set up from the model by either creating a SimpleModelicaExperimentDefinition class by passing the model
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

The simulation options can be set up as shown below::

   simulation_options = dynamic.get_simulation_options().with_values(ncp=500)
   solver_options = {'atol':1e-8}
   experiment_definition = model.new_experiment_definition(
       dynamic.with_parameters(start_time=0.0, final_time=2.0),
       solver_options=solver_options,
       simulation_options=simulation_options
   )

It is also possible to setup a series of experiments as shown below::

   from modelon.impact.client import Range

   experiment_definition = experiment_definition.with_modifiers({'PI.k': Range(10, 100, 3)})

This would setup an experiment with 3 cases. Please refer the :doc:`multi-execution <multi_execution_experiments>` tutorial for more information on this.

Executing the experiment
************************

Following either of the approaches listed below, the experiment definition set up could be executed:

One step execution
##################
The experiment definition set up can now be passed to the ``execute()`` function::

   experiment = workspace.execute(experiment_definition).wait()

This approach couples both the creation and execution of the experiment in one step.

Two step execution
##################
This approach isolates the creation and execution of an experiment as two methods::

   experiment = workspace.create_experiment(experiment_definition)
   experiment = experiment.execute().wait()

The benefit of this approach is that it allows the execution of a subset of the cases by passing them as
a list in the ``with_cases`` argument to the ``execute`` function. This is covered in detail :ref:`here<Filtered case execution>`.

**Note:**

We have called the ``wait()`` method after the ``execute()`` method to ensure that the execution process reaches completion.
If ``wait()`` is not called on the model an ``Operation`` object is returned and ``is_complete()`` can be used to check the status of the
execution. Calling the ``wait()`` method returns a ``Experiment`` object upon completion of the execution.
