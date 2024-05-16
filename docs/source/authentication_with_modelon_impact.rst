Authentication with Modelon Impact
==================================

This page explains how to authenticate and login to a Modelon Impact server from the Python client 
in various environments.

The cloud and on-premises Modelon Impact REST API for non-browser clients relies on an API key for authentication.
In order to work with the API, client code needs to pass ``impact-api-key: <api key>`` header with all requests. 
The `Client()` will initialize this header by default using the value of ``MODELON_IMPACT_CLIENT_API_KEY`` 
environment variable.

The ``MODELON_IMPACT_CLIENT_API_KEY`` environment variable is automatically set with a temporary user 
specific API key inside the Modelon Impact environment. Therefore explicit user input is not needed 
when the Python client is used in a script, notebook or custom function running within the Modelon Impact 
by a logged in user.

The Python client could be easily initialized as follows for a user accessing the client library 
from inside Modelon Impact:

.. code-block:: pycon

    >>>> from modelon.impact.client import Client
    >>>> client = Client()

The next session explains the process of generating and using API key when 
scripting with Python client from outside Modelon Impact, e.g., from a desktop.


Modelon Impact API key generation
#################################

An API key is needed for authentication in order to utilize the client with the Modelon Impact server.  

To generate the key, go to the `Server Management <https://help.modelon.com/latest/reference/jupyterhub_advanced_tools/#server-management>`_
on Modelon Impact. Click on the ``IMPACT API KEY`` tab drop-down and click ``Regenerate and replace key``
to generate a new one.

*Remember that this is the only time you will see the secret. Make sure to store it
safely.*

Copy the key and keep it safe. If the key is lost or compromised, you can generate 
a new one by clicking the ``Regenerate and replace key`` button. This will delete 
the old key, so any application that uses it must have their keys updated to work. 
The API key is personal and each user may have one single key at a time,
so do not share one key between several persons.

The API key may be passed into the `Client()` constructor either
via an environment variable, a key file or interactively.

1. Environment variable
+++++++++++++++++++++++

The environment variable ``MODELON_IMPACT_CLIENT_API_KEY`` can be set to contain the ``api_key`` 
string value.

2. Credentials file
+++++++++++++++++++

API key may be stored in a credentials file named ``api.key`` located in the directory
``~/.impact`` in the users home folder. The client class will look for the key there if
the key is not set as an environment variable.

This file is also used by the client to store the key in interactive mode and might be
overwritten, see :ref:`interactive<3. Interactive>`.

3. Interactive
++++++++++++++

The interactive mode is useful when running an interactive Python shell. Initialize the
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
The API key used to authenticate Modelon Impact is looked up in the following preference order:

1. API key saved in the environment variable - ``MODELON_IMPACT_CLIENT_API_KEY``
2. API key saved in the user's ``~/.impact/api.key`` file.
3. API key set via interactive prompt (if ``interactive`` is set to True)
