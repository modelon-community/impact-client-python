Install Modelon Impact Client
=============================

You can install Modelon Impact Client with ``pip``, or by installing from source. To locate a Python client version
that works with your version of Modelon Impact, refer to the 
:ref:`compatibility <Modelon Impact Vs Python client version compatibility map>` mapping.

Pip
---

You can install the client with ``pip``::

   pip install modelon-impact-client

Conda
-----

The modelon-impact-client package is not hosted on any conda channels. However, you can still install the client 
with ``conda`` using :ref:`pip <Pip>`. Refer 
to `using pip in an environment <https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#using-pip-in-an-environment>`_
for instructions.

Install from Source
-------------------

The client library is actively developed on GitHub. To install Modelon Impact Client from source, clone the repository from `GitHub
<https://github.com/modelon-community/impact-client-python>`_::

    git clone https://github.com/modelon-community/impact-client-python.git
    cd impact-client-python
    python -m pip install .

Requirements
------------

Modelon Impact Client supports Python versions 3.9 or higher. The client library is developed in sync with 
Modelon Impact and is kept updated with the latest changes in the tool.

Modelon Impact Vs Python client version compatibility map
---------------------------------------------------------

+-------------------------+--------------------------------------------------+
| Modelon Impact version  |            Python client version                 |
+=========================+==================================================+
|         1.1.x           | 1.1.x (pip install modelon-impact-client~=1.1.0) |
+-------------------------+--------------------------------------------------+
|         1.5.x           | 1.2.x (pip install modelon-impact-client~=1.2.0) |
+-------------------------+--------------------------------------------------+
|  1.8.x, 1.9.x, 1.10.x   | 2.4.x (pip install modelon-impact-client~=2.4.0) |
+-------------------------+--------------------------------------------------+
|         2.8.x           | 3.0.x (pip install modelon-impact-client~=3.0.0) |
+-------------------------+--------------------------------------------------+
|         2.9.x           | 3.0.x (pip install modelon-impact-client~=3.0.0) |
+-------------------------+--------------------------------------------------+
|         3.15.x          | 4.0.x (pip install modelon-impact-client~=4.0.0) |
+-------------------------+--------------------------------------------------+