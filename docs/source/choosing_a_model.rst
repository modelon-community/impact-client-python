Choosing a model
================

*This tutorial sections covers choosing a model to use for analysis.*

We can either choose a model from a library pre-loaded in Modelon Impact or upload a model to our workspace. To upload
a model to our workspace, we can pass the path to the modelica file::

   workspace.upload_model_library('C:/Model.mo')
   model = workspace.get_model("Model")

or choose a model from a pre-loaded library, like ``Modelica Standard Library``::

   model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")

This will return an instance of a ``Model`` class object. This ``Model`` class
will be used as input for creating an experiment.