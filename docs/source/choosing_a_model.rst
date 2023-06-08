Choosing a model
================

*This tutorial sections covers choosing a model to use for analysis.*

Modelica models and libraries are available in Modelon Impact within projects. We can either choose a model 
from a preloaded Modelica project in Modelon Impact or import a Modelica model or library to our default
project. To import a model to our workspace, we can pass the path to the Modelica file::

   project = workspace.get_default_project()
   
   # Upload a single Modelica model file
   modelica_content = project.import_modelica_library('LibA.mo').wait()
   model = workspace.get_model("LibA.Model")

   Or

   # Upload a zipped modelica library
   modelica_content = project.import_modelica_library('LibB.zip').wait()

   model = workspace.get_model("LibB.Model")

or choose a model from a preloaded library, like ``Modelica Standard Library``::

   model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")

This will return an instance of a ``Model`` class object. This ``Model`` class
will be used as input for creating an experiment.
