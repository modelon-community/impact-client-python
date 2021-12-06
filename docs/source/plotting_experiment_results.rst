Plotting experiment results
===========================

*This tutorial sections covers plotting the results of an experiment.*

Once the experiment execution completes, we can plot the result trajectories from the simulation.
To fetch the case trajectories for a given experiment the ``get_cases()`` method can be 
called on the experiment and further it could be checked if the cases did simulate successfully by calling
the ``is_successful()`` method on the case. The ``get_trajectories()`` function can be called on the individual ``case`` objects to
fetch the ``Result`` class object for that specific case.

To plot the results, the variable names of interest could be passed as index variables on the ``Result`` class object::

   import matplotlib.pyplot as plt

   plt.figure(1)
   plt.clf()
   for case in experiment.get_cases():
      if case.is_successful():
         result = case.get_trajectories()
         plt.plot(result['time'], result['inertia1.phi'])
   plt.grid()
   plt.show()

If the user wishes to fetch many result variables together, the below workflow could be followed::

   result = experiment.get_trajectories(['inertia1.phi', 'time'])
   height_1 = result['case_1']['inertia1.phi']
   time_1 = result['case_1']['time']
   height_2 = result['case_2']['inertia1.phi']
   time_2 = result['case_2']['time']
   height_3 = result['case_3']['inertia1.phi']
   time_3 = result['case_3']['time']
