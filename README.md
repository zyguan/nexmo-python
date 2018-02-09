Nexmo Client Library for Python
===============================

[![PyPI version](https://badge.fury.io/py/nexmo.svg)](https://badge.fury.io/py/nexmo) [![Build Status](https://api.travis-ci.org/Nexmo/nexmo-python.svg?branch=ng)](https://travis-ci.org/Nexmo/nexmo-python)

This is the Python client library for Nexmo's API. To use it you'll
need a Nexmo account. Sign up [for free at nexmo.com][signup].

* [Installation](#installation)
* [Usage](#usage)
* [License](#license)

The NG Manifesto
----------------

The `ng` branch (stands  for Next Generation) is an experimental branch to play with ideas about where we want the library to go. The principles used to guide this branch are:

* **Pythonic**: No need to use dicts where a well-designed class is better. Sensible defaults. Arguments provided *as* parameters to functions.
* **Python 3 Only**: We're not going to compromise on the library by supporting Python 2. At the moment we're targeting Python 3.5+
* **Type Hints**: Type hints can really help users in using the library correctly, so the public interface will be heavily annotated with type hints.
* **A Rich Client Library**: Some of Nexmo's older APIs have slightly crufty data structures. This library will convert between those values and the expected native Python types. Abstractions will be provided for API data structures such as webhook payloads and NCCO structures.

Installation
------------

To install the Python client library using pip:

    pip install nexmo

Alternatively you can clone the repository:

    git clone git@github.com:Nexmo/nexmo-python.git

Usage
-----

Let's shake this thing up!

Contributing
------------

We :heart: contributions! But if you plan to work on something big or controversial, please [contact us](mailto:devrel@nexmo.com) first!

We recommend working on `nexmo-python` with [pipenv][pipenv]. The following command will install all the Python dependencies you need to run the tests:

```bash
make install
```

The tests are all written with pytest. You run them with:

```bash
make test
```


License
-------

This library is released under the [MIT License][license]

[pipenv]: https://github.com/pypa/pipenv
[report-a-bug]: https://github.com/Nexmo/nexmo-python/issues/new
[pull-request]: https://github.com/Nexmo/nexmo-python/pulls
[signup]: https://dashboard.nexmo.com/sign-up?utm_source=DEV_REL&utm_medium=github&utm_campaign=python-client-library
[license]: LICENSE.txt
