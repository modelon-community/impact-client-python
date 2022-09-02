Setup
=====

This page describes the procedure to set up API keys to authenticate your login and
various ways to use the generated API key to log in to the client.

Authentication with JupyterHub
******************************

This section is ONLY applicable for users running Modelon Impact in a JupyterHub environment,
otherwise skip to the section :ref:`below<Authentication with API keys>`.
To use the client on JupyterHub, the users needs to first authenticate with a token
for Jupyterhub. To generate the key, go to the JupyterHub token manager 
(located at <JupyterHub url>/token).You can get a secret token by clicking the 
"Request new API token" button. These are tokens with full access to the JupyterHub API. 
Anything you can do with JupyterHub can be done with these tokens.

*Remember that this is the only time you will see the secret. Make sure to store it
safely.*

If the token is lost, you can always generate a new one by clicking the "Request new API token"
button.
While initializing the client, you will be asked to enter the JupyterHub API token in a prompt.

.. code-block:: pycon

    >>>> from modelon.impact.client import Client
    >>>> client = Client(url=<JupyterHub url>, interactive=True)
    Enter JupyterHub API token:

When the token has been entered the first time, it will be stored and used in future requests, 
and the prompt will not be shown again. To view a list of active tokens or revoke active tokens, 
the user can go to the JupyterHub token manager (located at <JupyterHub url>/token).
Revoking the token will cause the prompt to be shown again and a new token needs to be created.
Once the JupyterHub API has been authenticated, the user need to authenticate the client for Modelon Impact 
following the section :ref:`below<Authentication with API keys>`.

For non-interactive usage, the API token can be set as the ``MODELON_IMPACT_JUPYTERHUB_CLIENT_API_TOKEN`` environment variable.

Authentication with API keys
****************************

To use the client, authentication with an API key is required. To generate the key, go
to the API key manager (located at <impact url>/admin/keys/). You will get a secret
API key and a key ID. The API key is personal and each user may have one single key at
a time, so do not share one key between several persons.

*Remember that this is the only time you will see the secret. Make sure to store it
safely.*

If the key is lost or compromised, you can generate a new one by clicking the refresh
button. This will delete the old key, so any application that uses it must have their
keys updated to work.

There are several ways to use the API key, depending on how it is stored. It can either
set as an environment variable, saved in a key file or entered interactively.


Environment variable
####################

The ``api_key`` can be set as the environment variable ``MODELON_IMPACT_CLIENT_API_KEY``.


Credentials file
################

It may also be stored in a credentials file named ``api.key`` located in the directory
``.impact`` in the users home folder. The client class will look for the key there if
the key is not set as an environment variable.

This file is used by the client to store the key in interactive mode and might be
overwritten, see :ref:`interactive-mode`.


.. _interactive-mode:

Interactive
###########

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

.. _the API key manager: /admin/keys/
