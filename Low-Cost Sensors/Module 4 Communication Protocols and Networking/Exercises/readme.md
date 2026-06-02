# Module 5: Communication Protocols and Networking

## Coding examples
These are the coding examples for the Communications and Networking module. Since these examples are working with server and with communication, the examples are not done as iPhyton Notebooks, but as Python scripts. You need to install a Python distribution on your computer to make it work:
* The recommended Python distribution is Conda-forge with the [miniforge installer](https://github.com/conda-forge/miniforge/releases). You find installation packages for Windows, MacOS and a few Linux systems. If you have already another Python distribution installed, you can of course use the version you have installed
* I need something to edit Python source files. You can use a simple text editor, but there are also Python IDEs availble, like [PyCharm](https://www.jetbrains.com/pycharm/), [Visual Studio Code with a Python Interpreter](https://code.visualstudio.com/docs/python/python-tutorial) or [Spyder](https://docs.spyder-ide.org/). If you installed conda-forge with the miniforge installer just before, you can install the minimal Spyder environment with:
```
conda create -c conda-forge -n spyder-env spyder
```
or the full Spyder IDE with:
```
conda create -c conda-forge -n spyder-env spyder numpy scipy pandas matplotlib sympy cython
```
* You need to install a few packages to run all the examples:
    * FastAPI:
        * PIP: `pip install "fastapi[standard]"`
        * conda: `conda install conda-forge::fastapi[standard]`
    * Pydantic:
        * PIP: `pip install pydantic`
        * conda: `conda install conda-forge::pydantic`
    * Requests:
        * PIP: `pip install requests`
        * conda: `conda install conda-forge::requests`
    * Eclipse Paho MQTT:
        * PIP: `pip install paho-mqtt`
        * conda: `conda install conda-forge::paho-mqtt`

## First simple HTTP server
The first example is the file `01_simple_server.py` this file is already complete and creates the first, most simple HTTP possible. All you have to to do is to navigate to the file either in the command prompt or in the IDE and start it. In the command prompt you can start the server with
```
fastapi run ./01_simple_server.py --port 8080
```
Now, if you open the `http://localhost:8080/hello` in your browser, you will see the response from the server


## Call counter
In the next example, you should modify the code of the first simple HTTP server to create a counter, that is counting how often the page was visited. There is no need for persistence, the counter can be implemented as a simple variable in the memory of the server.

You find the solution in the file `02_counter.py`, which can be started with
```
fastapi run ./02_counter.py --port 8080
```
And you see the counter if you refresh the page `http://localhost:8080/hello` in your browser


## Path parameters
Now we will add some path parameters to the code. You find the example in the file `03_path_parameter.py`. This file can be run by 
```
fastapi run ./03_path_parameter.py --port 8080
```

By entering the following address in the browser, you will see the response from the server
```
http://localhost:8080/parameters/hello/123
```
However, if you change the parameters in the browser, the request will fail
```
http://localhost:8080/parameters/123/hello
```

Now change the code that the path parameters are switched round, i.e., the second request works and the first request fails.

## Query parameters
The file `04_query_parameter.py` shows you how query parameters can be implemented. Query parameters have much more flexibility compared to path parameters. The file can be run by 
```
fastapi run ./04_query_parameter.py --port 8080
```
There are four possible request done from the browser:
* `http://localhost:8080/required?name=hello&value=123.4`: Both parameters are required, if you delete one, the request will fail
* `http://localhost:8080/optional?name=hello`: Value is optional, it can be given but it will be `None` if there is no value given
* `http://localhost:8080/default?name=hello`: Value is optional, it can be given but it will be `12.34` if there is no value given


Now introduce a new end point called `combined` where the parameter `name` is given as a path parameter and the parameter `value` is optional with a default value von `32.1`

## Sending complex data with POST requests
Until now, we where only sending data via POST request. This only works for limited data, since the queries are getting quite long, if much data is send. However, it is easy for us to send more data with POST requests, update data with PUT request and delete data with DELET requests. A simple server implementation can be found in the file `05_server.py`:
* GET request show what data is already on the server
* POST request can add new data
* PUT requests can modify data
* DELETE requests delete data

To ensure that the data we get is properly formatted in JSON strings, we use Pydantic: This package takes a class definition (see line 16 to 18) and enforces this format to all data we get in the POST and PUT requests.

As a next step we implement the client. You can look at the file `05_client.py` to see the client. We use the requests-package to send data to the server. The data is JSON encoded. The client implements all methods with GET, POST, PUT, and DELET requests.

The server can be run with 
```
fastapi run ./05_server.py --port 8080
```
and the client script can be started with a python interpreter
```
python ./05_client.py
```

## MQTT publish and subscribe messages
After the HTTP examples, we are now moving to MQTT. There are two files provided for this:
* `06_subscribe.py` 
    * This is a script that subscribes to messages from a broker
    * It can be started with `python ./06_subscribe.py` and then keeps on running
* `06_publish.py`
    * This script sends one messages to the broker
    * It can be started with `python ./06_publish.py` and finishes after the messaged has been send

These two scripts are the basis to explore the MQTT functionality so that you can:
* Modify the subscription and publishing topics
    * Try to use wild cards for the subscription
* Change the data that is send
* Use different brokers
* Use different QoS
* Use different MQTT versions
* Send multiple messages
