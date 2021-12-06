Choosing analysis type
======================

*This tutorial sections covers choosing an analysis methods required for setting up an experiment in Modelon Impact.*

Once we have our ``Workspace`` setup, we need to choose an analysis method to fetch the different options available
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

This will return an instance of a ``dynamic`` ``CustomFunction`` class object. This ``CustomFunction`` class 
will be used as input for creating an experiment.
