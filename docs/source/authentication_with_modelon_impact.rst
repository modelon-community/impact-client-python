Authentication with Modelon Impact
==================================

This page explains how to authenticate and login to the Modelon Impact server from the Python client 
in various environments.

The cloud/on-premise architecture for Modelon Impact uses JupyterHub as one of its components. 
As a consequence, when connecting via an external URL like https://impact.modelon.cloud, 
JupyterHub gateway authentication is necessary. From a notebook that is active within the MI 
installation, one can create a connection to the external URL. In that case, this will be automatic
based on the automatically populated ``JUPYTERHUB_API_TOKEN`` environment variable.

An API key must be used in addition to the ``JUPYTERHUB API TOKEN`` to authenticate against the Modelon 
Impact server operating inside the JupyterHub environment. If the client library is used within the
JupyterHub environment, this is likewise handled automatically based on the key stored at 
``~/.impact/api.key`` in that environment.

The python client could be easily initialized as follows for a user accessing the client library 
in the JupyterHub environment:

.. code-block:: pycon

    >>>> from modelon.impact.client import Client
    >>>> client = Client()


JupyterHub authentication
*************************

**Note**:- This section is **ONLY** applicable for users using the client library used outside of
the JupyterHub environment.

If this client library is used outside of the environment, such as from your desktop, the JupyterHub API 
token must be provided either interactively or in the environment variable ``JUPYTERHUB_API_TOKEN``. The token
can be acquired using the token page at https://impact.modelon.cloud/hub/token or a similar page in the 
on-premise installation. The below sections will cover details to generate an API key to log in to the 
client.

JupyterHub token generation
###########################

To create the JupyterHub token, go to the JupyterHub token manager (located at "https://impact.modelon.cloud/hub/token"). 
You can get a secret token by choosing the "Request new API token" option. These are fully functional access tokens for 
the JupyterHub API. Everything that can be done with JupyterHub can be done with these tokens.

*Remember that this is the only time you will see the secret. Make sure to store it safely.*

If the token is lost, you can always generate a new one by clicking the "Request new API token"
button. While initializing the client, you will be asked to enter the JupyterHub API token in a prompt.

.. code-block:: pycon

    >>>> from modelon.impact.client import Client
    >>>> client = Client(url="https://impact.modelon.cloud", interactive=True)
    Enter JupyterHub API token:

When the token has been entered the first time, it will be stored at located in the directory
``~/.impact`` in the users home folder as 'jupyterhub-api.key' and used in future requests and the prompt will not be 
shown again. 

Another option is to save the token in the environmental variable ``JUPYTERHUB_API_TOKEN``, which 
would allow the client to authenticate without engaging in any interaction prompts.

To view a list of active tokens or revoke active tokens, the user can
go to the JupyterHub token manager (located at "https://impact.modelon.cloud/hub/token").
Revoking the token will cause the prompt to be shown again and a new token needs to be created.

After authenticating against the JupyterHub API, the user must also authenticate against the Modelon Impact server 
by following the instructions in the section :ref:`below<Modelon Impact API key generation>`.

**Note:**
The token used to authenticate JupyterHub is looked up in the following preference order:-

1. Token set via interactive prompt
2. Token saved in the environment variable - ``JUPYTERHUB_API_TOKEN``
3. Token saved in file - ~/.impact/jupyterhub-api.key

Modelon Impact API key generation
#################################

An API key is needed for authentication in order to utilize the client with the Modelon Impact server.  
To generate the key, go to the `Server Management <https://help.modelon.com/latest/reference/jupyterhub_advanced_tools/#server-management>`_
on Modelon Impact. Click on the ``IMPACT API KEY`` tab drop-down and click `Regenerate and replace key``
to generate a new one.

*Remember that this is the only time you will see the secret. Make sure to store it
safely.*

Copy the key and keep it safe. If the key is lost or compromised, you can generate 
a new one by clicking the ``Regenerate and replace key`` button. This will delete 
the old key, so any application that uses it must have their keys updated to work. 
The API key is personal and each user may have one single key at a time,
so do not share one key between several persons.

Depending on how it is stored, there are many ways to use the API key. 
It can be typed interactively, assigned as an environment variable, or saved in a key file.

1. Environment variable
+++++++++++++++++++++++

The environment variable ``MODELON_IMPACT_CLIENT_API_KEY`` can be used to set the ``api_key``.

2. Credentials file
+++++++++++++++++++

It may also be stored in a credentials file named ``api.key`` located in the directory
``~/.impact`` in the users home folder. The client class will look for the key there if
the key is not set as an environment variable.

This file is used by the client to store the key in interactive mode and might be
overwritten, see :ref:`interactive<3. Interactive>`.

3. Interactive
++++++++++++++

The interactive mode is useful when running an interactive python shell. Initialize the
client with the ``interactive`` keyword set to True. If the environment variable is not
set and the credentials file does not exist you will be asked to enter the API key in a
prompt.

.. code-block:: pycon

    >>>> from modelon.impact.client import Client
    >>>> client = Client(url=impact_url, interactive=True)
    Enter API key:


When the key has been entered the first time, it will be stored in the credentials file
to be used in future requests, and the prompt will not be shown again. If the key is
changed, the file may be deleted which will cause the prompt to be shown again.

The stored API key can also be modified using the ``CredentialManager`` class.

.. code-block:: pycon

    >>>> from modelon.impact.client.credential_manager import CredentialManager
    >>>> credential_manager = CredentialManager()
    >>>> credential_manager.get_key_from_file()
    'some-old-api-key'
    >>>> credential_manager.write_key_to_file('my-new-key')
    >>>> credential_manager.get_key_from_file()
    'my-new-key'

**Note:**
The API key used to authenticate Modelon Impact is looked up in the following preference order:-

1. API key set via interactive prompt
2. API key saved in the environment variable - ``MODELON_IMPACT_CLIENT_API_KEY``
3. API key saved in file - ~/.impact/api.key
