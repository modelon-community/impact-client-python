Setting up the workspaces
=========================

*This tutorial sections covers initializing the client with the Impact domain and setting
up a workspace.* 

An API key is required to authenticate our login to the server. Refer to the 
steps listed in the :doc:`Setup <setup>` section to configure an API key::

   from modelon.impact.client import Client

   client = Client(url=<impact-domain>)

Once the client is initialized, we can either create a workspace::

   workspace = client.create_workspace(<workspace-name>)

or upload an existing workspace by specifying the path to the compressed workspace(.zip) to be uploaded::

   workspace = client.upload_workspace(<path_to_workspace>)

This will return an instance of a ``Workspace`` class object with the same name as the zip-file (and
a number appended if another workspace with the same name already exists).