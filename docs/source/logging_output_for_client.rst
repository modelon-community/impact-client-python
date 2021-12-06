Logging output for client
=========================

*This tutorial covers setting logging options to control the amount of information output by the client.*

The built-in python module, ``logging`` (https://docs.python.org/3.9/library/logging.html) is used by the client. The amount of logging that
should be output by the client can be set by specifying the log level as shown in the code snippet::

   import logging

   logging.getLogger('modelon.impact.client').setLevel(logging.ERROR)

The log is printed to the standard output, normally the terminal window from which the python interpreter is invoked. The available log levels are
'INFO'(default), 'ERROR', 'WARNING', 'CRITICAL' and 'DEBUG'.
