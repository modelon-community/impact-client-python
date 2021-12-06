Removing FMUs and experiments
=============================

*This tutorial sections covers removing the FMUs and experiments in a workspace to free 
up disk space.*

The below code snippet could be used to delete all the FMUs and experiments in a workspace::

   experiments = workspace.get_experiments()
   fmus = workspace.get_fmus()

   for experiment in experiments:
      experiment.delete()
    
   for fmu in fmus:
      fmu.delete()

**Note:** The FMUs and generated result cannot be restored after running this code.