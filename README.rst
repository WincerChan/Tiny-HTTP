===============
Tiny HTTP
===============

|Python-version| |License|

.. |Python-version| image:: https://img.shields.io/badge/python-%3E=3.5-0e83cd.svg?style=flat-square   :alt: Python Version
.. |License| image:: https://img.shields.io/badge/License-GPL%20v3-blue.svg?style=flat-square   :alt: License


Introduction
==============
A socket-based static HTTP server, Support for asynchronous.(Does not support python2)
  
Install
==============
``pip install tinyhttp``

Usage
==============
Asynchrous
  
``python -m tinyhttp # or tinyhttp``

Multi-Thread

``python -m tinyhttp.thread``

Set Port(The defalut port is 6789.)


``python -m tinyhttp.thread 6666``

Debug mode

``python -m tinyhttp --debug``
