Quick Start
===========

The python API enables the execution of workflows orchestrated on a client and executed on a Modelon Impact server, which
may be running remotely.  With sufficient login credentials and an API Key (see :doc:`Setup <setup>`),
Modelica models may be uploaded, compiled, and executed on a server.  The results can be either processed on the server
with a custom function or downloaded to the client for further analysis.

An analysis could be set up and executed using either the :ref:`FMU <FMU based workflow>` or a :ref:`Class name <Setup and run an experiment>` based workflow.

A simple example using the :ref:`FMU based workflow <FMU based workflow>` is shown below::

   from modelon.impact.client import Client

   client = Client(url=<impact-domain>)
   workspace = client.create_workspace(<workspace-name>)

   # Choose analysis type
   dynamic = workspace.get_custom_function('dynamic')

   # Compile model
   model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")
   fmu = model.compile(compiler_options=dynamic.get_compiler_options()).wait()

   # Execute experiment
   experiment_definition = fmu.new_experiment_definition(dynamic)
   exp = workspace.execute(experiment_definition).wait()

   # Plot Trajectory
   import matplotlib.pyplot as plt

   case = exp.get_case('case_1')
   res = case.get_trajectories()
   plt.plot(res['time'], res['inertia1.phi'])
   plt.show()

A simple example using the :ref:`Class name based workflow <Setup and run an experiment>` is shown below::

   from modelon.impact.client import Client

   client = Client(url=<impact-domain>)
   workspace = client.create_workspace(<workspace-name>)

   # Choose analysis type
   dynamic = workspace.get_custom_function('dynamic')

   # Get model class
   model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")

   # Execute experiment
   experiment_definition = model.new_experiment_definition(dynamic)
   exp = workspace.execute(experiment_definition).wait()

   # Getting the simulated FMU object from the case object
   case = exp.get_case('case_1')
   fmu = case.get_fmu()

   # Plot Trajectory
   import matplotlib.pyplot as plt

   res = case.get_trajectories()
   plt.plot(res['time'], res['inertia1.phi'])
   plt.show()

An example of setting up and executing a series of simulations on a server and returning the plot trajectories::

   from modelon.impact.client import Client, Range

   client = Client(url=<impact-domain>)
   workspace = client.create_workspace(<workspace-name>)

   # Choose analysis type
   dynamic = workspace.get_custom_function('dynamic')

   # Get model
   model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")

   # Execute experiment
   experiment_definition = model.new_experiment_definition(
      dynamic.with_parameters(start_time=0.0, final_time=2.0),
      simulation_options=dynamic.get_simulation_options().with_values(ncp=500),
      solver_options={'atol': 1e-8},
   ).with_modifiers({'inertia1.J': 2, 'PI.k': Range(10, 100, 3)})
   exp = workspace.execute(experiment_definition).wait()

   # Getting a set of simulated FMU objects from the cases
   fmus = set(case.get_fmu() for case in exp.get_cases())

   # Plot Trajectory
   import matplotlib.pyplot as plt

   plt.figure(1)
   plt.clf()
   for case in exp.get_cases():
      if case.is_successful():
         res = case.get_trajectories()
         plt.plot(res['time'], res['inertia1.phi'])
   plt.grid()
   plt.show()

A more flexible and customized way to define a series of simulations::

   from modelon.impact.client import Client, SimpleExperimentExtension

   client = Client(url=<impact-domain>)
   workspace = client.create_workspace(<workspace-name>)

   # Choose analysis type
   dynamic = workspace.get_custom_function('dynamic')

   # Get model
   model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")

   experiment_definition = model.new_experiment_definition(
      dynamic.with_parameters(start_time=0.0, final_time=2.0),
      simulation_options=dynamic.get_simulation_options().with_values(ncp=500),
      solver_options={'atol': 1e-8},
   ).with_modifiers({'inertia1.J': 2})

   simulate_ext1 = SimpleExperimentExtension(
      {'final_time': 5}, {'atol': 1e-7}
   ).with_modifiers({'PI.k': 40})
   simulate_ext2 = SimpleExperimentExtension().with_modifiers({'PI.k': 50})

   experiment_definition = experiment_definition.with_extensions(
      [simulate_ext1, simulate_ext2]
   )

   experiment_definition = experiment_definition.with_cases([{'PI.k': 20}, {'PI.k': 30}])

A workflow to fetch artifacts to do some analysis locally could be accomplished like below::

   from modelon.impact.client import Client

   client = Client(url=<impact-domain>)
   workspace = client.create_workspace(<workspace-name>)

   # Compile and download model
   model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")
   fmu = model.compile({'c_compiler': 'gcc'}).wait()
   fmu_path = fmu.download()

   # Use PyFMI or other tools that work with FMUs
   from pyfmi import load_fmu

   fmu_model = load_fmu(fmu_path)
   res = fmu_model.simulate()
   ...

**Note:**

The OS running the Impact server must match the environment that runs the compiled FMU. This is necessary as the binaries
packaged with the FMU are based on the platform generating the FMU. For example, if the Impact server is running Linux
the binary in the downloaded FMU is compiled for Linux. The downloaded FMU can then not be simulated on Windows.
