# I like trains game

![Thumbnail](img/thumbnail_2.png)

## Requirement

- Python 3.10

## Creation of a virtual environment

To create a virtual environment, follow the steps below:

### Create a virtual environment in the folder (do it once after cloning the project)
`python -m venv venv`
 
### Activate the virtual environment (every time before starting the project)
#### On windows
`.\venv\Scripts\activate`

#### On macOS/Linux
`source venv/bin/activate`

## Dependencies installation

After activating the virtual environment, install the necessary dependencies:

`pip install -r requirements.txt`

## Project execution

To execute the project, use the following command:
`python client.py`

## Logging System

The game uses Python's built-in logging system to help with debugging and monitoring. Change the logging level in the `logging.basicConfig` function in the `agent.py` file.

Available log levels (from most to least verbose):
- DEBUG: Detailed information for debugging
- INFO: General information about game operation
- WARNING: Indicates potential issues
- ERROR: Serious problems that need attention
- CRITICAL: Critical errors that prevent the game from running

Logs are displayed in the console and include timestamps, module name, and log level.