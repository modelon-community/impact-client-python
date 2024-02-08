Working with workspaces
=======================

*This tutorial sections covers creating workspace, fetching existing one and sharing them.*

**Prerequisite**

An API key is required to authenticate our login to the server. Refer to the 
steps listed in the :doc:`Authentication with Modelon Impact<authentication_with_modelon_impact>` 
section to configure an API key::

   from modelon.impact.client import Client

   client = Client(url=<impact-domain>) # url is optional; defaults to on-prem OR "https://impact.modelon.cloud"

Once the client is initialized, we can create a workspace, use an existing workspace or upload one.

Workspaces
**********

In Modelon Impact, each workspace has a distinct ID that defaults to a slug of the workspace name.
The workspace name need not be unique and can consist of any string. It may have special 
characters, spaces, mixed case, emojis, etc. There could be multiple workspaces with the same name, 
but each one can be distinguished by its ID. Workspace ID is fixed on creation and does not change when 
a workspace is renamed.
   
We can either create a new workspace with a name::

   workspace = client.create_workspace(<workspace-name>)

Or get an existing one by specifying the ID of the workspace or the name of the workspace::

   # Get workspace by ID
   workspace = client.get_workspace(<workspace-ID>) 

   # Get a list of workspaces with the given name
   workspaces = client.get_workspace_by_name(<workspace-name>)
   workspace = workspaces[0]

or import an existing workspace by specifying the path to the compressed workspace(.zip) to be uploaded::

   workspace = client.import_workspace_from_zip(<path_to_workspace>).wait()

The above methods will return an instance of a ``Workspace`` class object. To get the ID of the workspace, 
you could call the ID property on the returned ``Workspace`` class object::

   workspace_id = workspace.id

To get a list of all the existing workspaces, you could do::

   workspaces = client.get_workspaces()

**Note:**
Since workspace names are not unique(ID's are), create or uploading a workspace with the same name as an existing one
would result in multiple workspaces being created with same name.

Workspace sharing
*****************

A workspace in Modelon Impact can be shared as a zipped artifact (snapshot) or as a workspace configuration.
A snapshot can be either stored in a cloud storage and shared with the other users of the same 
Modelon Impact site or downloaded as a zip file to the client system.
Workspace configuration is a json-serializable structure containing links to version controlled 
projects and preinstalled libraries. 

Published Workspaces
#######################

Publishing a workspace to cloud storage bundles all Projects with Modelica packages including resources,
results and FMUs. Publishing specifying a model will publish an app mode workspace::

   # Create an example workspace containing experiment result
   from modelon.impact.client import Client

   client = Client()
   workspace = client.create_workspace("PublishDemo")
   model = workspace.get_model("Modelica.Blocks.Examples.PID_Controller")
   dynamic_cf = workspace.get_custom_function("dynamic")
   exp_def = model.new_experiment_definition(dynamic_cf)
   experiment = workspace.create_experiment(exp_def).execute().wait()

   # Publish the workspace to cloud storage in app mode
   workspace.export(publish=True, class_path="Modelica.Blocks.Examples.PID_Controller").wait()

A published workspace can be found and imported by a user who has appropriate access rights::

   pwc = client.get_published_workspaces_client()
   published_workspace = pwc.find(name="PublishDemo")[0]
   imported_workspace = published_workspace.import_to_userspace()

The imported workspace will contain results that were bundled and experiment IDs will be kept intact::

   imported_experiment = imported_workspace.get_experiments()[0]
   assert imported_experiment.id == experiment.id

Repeated imports of the same workspace do not update the workspace in userspace. However,
If update was published receiver can get his copy overwritten by the update::

   updated_workspace = published_workspace.import_to_userspace(update_if_available=True)
   assert imported_workspace.id == updated_workspace.id    

Zipped(snapshot) export
#######################

A zipped archive export of the workspace bundles all Projects (with Modelica packages including resources, and also results and FMUs). 
This ZIP file can then be uploaded at another point. The below code snippet exports an existing workspace::

   # Get workspace by ID
   workspace = client.get_workspace(<workspace-ID>) 

   # Export the workspace as a zipped archive
   path_to_exported_workpace = workspace.export().wait().download_as('/home/user/workspace.zip')

**Note:**

The workspace is exported to a .zip file and by default it includes result files and compiled models(FMU's).
The exported workspace could then be imported::

   workspace = client.import_workspace_from_zip(path_to_exported_workpace).wait()

Workspace definition export
###########################

Workspaces could also be shared via 'definitions'. This approach creates a workspace definition that can be shared with other users.
This requires that all projects used in the workspace is either version controlled or a released project. A user could export the 
workspace definition as a json file::


   workspace = client.get_workspace(<workspace-ID>)
   # Create snapshot/shared definition
   shared_definition = workspace.get_shared_definition()

   # Write shared definition to file
   shared_definition_file_path = definition.to_file(<path_to_store_file>)

and share it with another user, who would then import the file::

   imported_workspace = client.import_from_shared_definition(shared_definition).wait()

Conflict resolution
+++++++++++++++++++

The import will fail if there are multiple possible matchings of local projects for a project. 
This could happen if say the version control URI in the shared workspace definition matched with multiple projects. 
In this case we need use the `get_project_matchings` method to get these matchings which can be used to resolve to an 
unequivocal 'selection'. Selections are used as (optional) input to `import_from_shared_definition` method. To select 
the preferred project, a user could select them interactively:: 

   # Interactive workflow
   matchings = client.get_project_matchings(imported_workspace_definition)
   selections = matchings.make_selections_interactive()
   imported_workspace = client.import_workspace_from_shared_definition(
      imported_workspace_definition, selections
   ).wait()

Or programmatically ::

   # Programatic workflow
   matchings = client.get_project_matchings(imported_workspace_definition)

   # Assume the first in list of matchings is good enough:
   selections = [entry.get_selection(index=0) for entry in matchings.entries]
   imported_workspace = client.import_workspace_from_shared_definition(
      imported_workspace_definition, selections
   ).wait()
