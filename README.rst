*************
Err Twilio Lookup
*************

An `err`_ plugin for retrieving data on phone numbers from `Twilio Lookup`_.


.. image:: https://travis-ci.org/RobSpectre/err-twilio-lookup.svg?branch=master
    :target: https://travis-ci.org/RobSpectre/err-twilio-lookup

.. image:: https://coveralls.io/repos/RobSpectre/err-twilio-lookup/badge.png?branch=master
    :target: https://coveralls.io/r/RobSpectre/err-twilio-lookup?branch=master


**Table of Contents**


.. contents::
    :local:
    :depth: 1
    :backlinks: none


Installation
===========

Install this `err`_ plugin using err's handy installation utilities by typing
the following into a room with your errbot.

.. code-block: bash
  
    !repos install https://github.com/RobSpectre/err-twilio-lookup


Then configure the bot with your `Twilio credentials`_.

.. code-block: bash
   
    !plugin config TwilioLookup {'TWILIO_ACCOUNT_SID': 'ACxxxx', 'TWILIO_AUTH_TOKEN':
    'yyyyyyyy'}


Totally lookup information about phone numbers.

.. code-block: bash

    !lookup 5108675309


Meta
============

* Written by `Rob Spectre`_
* Released under `MIT License`_
* Software is as is - no warranty expressed or implied.


.. _err: http://errbot.net/
.. _Twilio Lookup: https://www.twilio.com/docs/api/rest/lookups
.. _Rob Spectre: http://www.brooklynhacker.com
.. _MIT License: http://opensource.org/licenses/MIT
.. _pytest: http://pytest.org/latest/
.. _PEP8: http://legacy.python.org/dev/peps/pep-0008/
.. _Twilio credentials: https://www.twilio.com/user/account/
