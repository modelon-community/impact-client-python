Quick Start
===========

The python API enables the execution of workflows orchestrated on a client and executed on a Modelon Impact server, which
may be running remotely.  With sufficient login credentials and an API Key (see :doc:`Setup <setup>`),
Modelica models may be uploaded, compiled, and executed on a server.  The results can be either processed on the server
with a custom function or downloaded to the client for further analysis.  

A simple example of this functionality is::

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

An example of setting up and executing a series of simulations on a server and returning the plot trajectories::

   from modelon.impact.client import Client, Range

   client = Client(url=<impact-domain>)
   workspace = client.create_workspace(<workspace-name>)

   # Choose analysis type
   dynamic = workspace.get_custom_function('dynamic')

   # Compile model
   model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")
   fmu = model.compile(
      compiler_options=dynamic.get_compiler_options().with_values(
         generate_html_diagnostics=True
      )
   ).wait()

   # Execute experiment
   experiment_definition = fmu.new_experiment_definition(
      dynamic.with_parameters(start_time=0.0, final_time=2.0),
      simulation_options=dynamic.get_simulation_options().with_values(ncp=500),
      solver_options={'atol': 1e-8},
   ).with_modifiers({'inertia1.J': 2, 'PI.k': Range(10, 100, 3)})
   exp = workspace.execute(experiment_definition).wait()

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

A workflow to fetch artifacts to do some analysis locally could be accomplished like below::

   from modelon.impact.client import Client

   client = Client(url=<impact-domain>)
   workspace = client.create_workspace(<workspace-name>)

   # Compile and download model
   model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")
   fmu = model.compile({'c_compiler': 'gcc'}).wait().download()

   # Use PyFMI or other tool that works with FMUs
   from pyfmi import load_fmu

   m = load_fmu(fmu)
   res = m.simulate()
   ...

Note:
#####

The OS running the Impact server must match environment that runs the compiled FMU. This is neccessary as the binaries
packaged with the FMU are based on the platform generating the FMU. For example, if the Impact server is running Linux 
the binary in the downloaded FMU is compiled for Linux. The downloaded FMU can then not be simulated on Windows.