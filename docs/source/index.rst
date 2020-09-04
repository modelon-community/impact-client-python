Modelon Impact Client
=================================================

*Client library for easy scripting against Modelon Impact*

Python companion library for the Modelon Impact solution that helps with the following:

1.  Authentication against Modelon Impact
2.  Python object model around the concepts of REST API
3.  Enables custom workflows and automation


.. image:: images/client-server.svg
   :alt: Modelon Impact usage
   :width: 100%
   :align: center

Can be used for workflows entierly done server side

.. code-block:: python

   from modelon.impact.client import Client, Range

   client = Client(url=<impact-domain>)
   workspace = client.create_workspace(<project-workspace>)

   # Choose analysis type
   dynamic = workspace.get_custom_function('dynamic')
   dynamic_opts = dynamic.options()

   # Compile model
   model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")
   fmu = model.compile(
       dynamic_opts.with_compiler_options(generate_html_diagnostics=True)
   ).wait()

   # Execute experiment
   experiment_def = fmu.new_experiment_definition(
       dynamic.with_parameters(start_time=0.0, final_time=2.0),
       dynamic_opts.with_simulation_options(ncp=500),
    ).with_modifiers({'inertia1.J': 2, 'inertia2.J': Range(0.1, 0.5, 3)})
   exp = workspace.execute(experiment_def).wait()

   # Plot Trajectory
   import matplotlib.pyplot as plt
   case = next(iter([case for case in exp.cases() if case.is_successful()]))
   res = case.trajectories()
   plt.plot(res['time'], res['inertia1.phi'])
   plt.show()

Or be used to fetch artifacts to do some analysis locally

.. code-block:: python

   from modelon.impact.client import Client

   client = Client(url=<impact-domain>)
   workspace = client.create_workspace(<project-workspace>)

   # Compile and download model
   model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")
   fmu = model.compile({'c_compiler': 'gcc'}).wait().download()

   # Use PyFMI or other tool that works with FMUs
   from pyfmi import load_fmu

   m = load_fmu(fmu)
   res = m.simulate()
   ...

Installation
==================

You can install the client with ``pip``::

   pip install --extra-index-url https://artifactory.modelon.com/artifactory/api/pypi/pypi-release-local/simple modelon-impact-client


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules
   api_keys

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
