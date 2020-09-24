Setup
=====

This page describes the procedure to set up API keys to authenticate your login and
various ways to use the generated API key to log in to the client.


Authentication with API keys
----------------------------

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
be set as an argument when the client is initialized, set as an environment variable,
saved in a key file or entered interactively.


Initializer argument
####################

When initializing the client, you may specify the optional keyword argument ``api_key``
to specify which key to use.

.. code-block:: python

    from modelon.impact.client import Client

    client = Client(api_key=my_api_key)

With this method, the key can be stored and retrieved in any way. Remember not to store
the API key in your source code file.


Environment variable
####################

If the ``api_key`` argument is not specified in the initializer, it may be set as the
environment variable ``MODELON_IMPACT_CLIENT_API_KEY``.


Credentials file
################

It may also be stored in a credentials file named ``api.key`` located in the directory
``.impact`` in the users home folder. The client class will look for the key there if
the key is neither passed as an argument nor set as an environment variable.

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
Alternatively, the credentials file may be updated by specifying the ``api_key``
argument in interactive mode:

.. code-block:: pycon

    >>>> client = Client(url=impact_url, api_key='new-api-key', interactive=True)

This will remove the old key and add the new one to the credentials file. The stored
API key can also be modified using the ``CredentialManager`` class.

.. code-block:: pycon

    >>>> from modelon.impact.client.credential_manager import CredentialManager
    >>>> credential_manager = CredentialManager()
    >>>> credential_manager.get_key_from_file()
    'some-old-api-key'
    >>>> credential_manager.write_key_to_file('my-new-key')
    >>>> credential_manager.get_key_from_file()
    'my-new-key'

.. _the API key manager: /admin/keys/
