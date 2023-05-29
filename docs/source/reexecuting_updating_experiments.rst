Re-executing and updating experiments
=====================================

*This tutorial covers updating and re-executing individual cases in an experiment.*

Filtered case execution
***********************

It is possible to update and run a subset of cases in a batch simulation. Call the execute method on the 
experiment object with the ``with_cases`` argument set to a list of the cases that should be executed. 
Observe that if the experiment has not been executed yet it will not have any cases that we can access. 
To work around this we can first execute the experiment and specify that no cases should be executed::

   experiment = workspace.create_experiment(experiment_definition)
   experiment_expand = experiment.execute(with_cases=[]).wait()

This generate all the cases for a given experiment definition and compiles all FMUs needed for running the cases. 
But, no cases are executed when the ``execute`` method is called with an empty list argument.

Now, to execute only a subset of cases (say "case_2" and "case_3") in a batch simulation with 20 cases, we can 
just pass the case objects as a list to the ``with_cases`` argument::
   
   case_2 = experiment.get_case('case_2')
   case_3 = experiment.get_case('case_3')

   experiment = experiment.execute(with_cases=[case_2, case_3]).wait()

Updating cases
**************

The case input for a specific case in a batch simulation can be updated and the case can be re-executed.
The following input values could be updated:

1. Custom function parameters - E.g. - 'start_time', 'final_time' for a dynamic simulation.
2. Simulation and solver options - E.g. - 'ncp', 'atol' etc for a dynamic simulation.
3. Non-structural parameters - E.g. - 'PI.k' for the Modelica.Blocks.Examples.PID_Controller.

The code snippet below shows examples of values that can be updated in a case::

   case_2 = experiment.get_case('case_2')

   case_2.input.analysis.parameters = {'start_time': 0, 'final_time':10}
   case_2.input.analysis.simulation_options = {'ncp': 600}
   case_2.input.analysis.solver_options = {'atol': 1e-8}
   case_2.input.parametrization = {'PI.k': 120}

It is also possible to add custom labels to cases to either uniquely identify them or group them::
   
   case_2.meta.label = 'PID_Controller_k_120'

The cases with the set label can then be fetched by calling the ``get_cases_with_label`` method on
the experiment object which would return a list of cases objects with the specified label::

   PID_Controller_k_120_cases = experiment.get_cases_with_label('PID_Controller_k_120')

Once the updates to the case input are made, we can re-execute the case by calling the ``execute``
method on the case object::
   
   case_2.execute()


Initializing from results
*************************

It is possible to initialize a case or an experiment with a result from either another case, experiment
or an external file. Observe that the custom function must support initializing from a result. 
Of the default custom functions only the 'steady state' custom function supports this.
This is useful in cases where a converged steady-state result could be used to initialize a failed
steady-state simulation. The different possibilities to initialize are covered in the sections below.

Consider the following steady-state batch execution scenario for a model. The parametrization for the `sweep` parameter
results in 3 cases, where let's say a single case(case_2) in the batch simulation fails::

   experiment_definition = experiment_definition.with_modifiers({'sweep': Range(10, 100, 3)})
   experiment = workspace.create_experiment(experiment_definition)
   experiment = experiment.execute().wait() # Case 2 fails

We could try to resolve this by initializing the failed case with an appropriate case or result as covered in the sections below.

Initialize from case
####################

1. Via case entity
++++++++++++++++++

The following code snippet initializes a case from another case of a single or batch simulation::

   # Fetching the successful case
   case_1 = experiment.get_case('case_1')

   # Fetching the failed case
   case_2 = experiment.get_case('case_2')

   # Initializing from successful case
   case_2.initialize_from_case = case_1

   # Re-executing the case after initializing
   case_init_successful = case_2.execute().wait()

2. Via experiment extensions
++++++++++++++++++++++++++++

It is also possible to initialize from a case for an experiment extension. The following 
code snippet shows a simple example of this::

   experiment_extension = SimpleExperimentExtension(
      parameter_modifiers={'final_time': 2.0},
      solver_options={'atol': 1e-9},
      simulation_options=dynamic.get_simulation_options().with_values(ncp=1500),
   ).initialize_from(case_1)

   experiment = experiment_definition.with_extensions(
      [experiment_extension]
   )
   experiment.execute().wait()

**Note:** For this example, the case('case_1') used to initialize the experiment_extension
comes from another experiment unlike the :ref:`case entity<1. Via case entity>` approach
where the case used to initialize was from the same experiment.

Initialize from external result
###############################

It is possible to upload external result files to initialize a case from. This can now only be used 
for initializing from in a case and be used as an alternative to :ref:`initializing from another case <Initialize from case>`.
Currently, '.mat' files are supported for result import.

Here is a code snippet, where an external result is imported and used to initialize a case::

   result = workspace.upload_result(path_to_result="<path_to_result>/result.mat", label = 
            "result_to_init", description= "Converged result file").wait()
   
   # Initializing from external result
   case_2.initialize_from_external_result = result

   # Re-executing the case after initializing
   case_init_successful = case_2.execute().wait()


