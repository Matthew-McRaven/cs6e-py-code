# Important Python Concepts
## Generator Expressions

## \_\_methods\_\_

## Type hints


# Configuring your Development Environment
This project assumes you use [PyCharm Community Edition 2024.1](https://www.jetbrains.com/pycharm/download/?section=mac) or higher.

Experienced python developers will be able to interact with this project entirely through a well-configured terminal.

## Install Python
We require python 3.12 or higher for this project. 
See [Python's installation instructions](https://www.python.org/downloads/) for the best way to get python on your platform.

## Install UV
We use [uv](https://docs.astral.sh/uv/) to manage our third-party python dependencies.
The [linked documentation](https://docs.astral.sh/uv/getting-started/installation/) includes one-time installation instructions.

## Initializing a Python Instance

The following [documentation from PyCharm](https://www.jetbrains.com/help/pycharm/configuring-python-interpreter.html#add_new_project_interpreter) walks through the details of adding a new python interpreter/runtime to PyCharm.
During this process, we will notify PyCharm of the location of our python binary, and our package manager, uv.

![Here's a video of me adding a python interpreter instance to PyCharm.](https://github.com/user-attachments/assets/6c6475ea-878a-4a2d-b5c5-394a6f296523)

**After setting up the project's interpreter, open up the IDE's terminal and execute `uv sync` to download all dependencies.**
Failure to run this command will cause future terminal commands to fail.

## Helpful Terminal Commands

| Task                    | Command    |
|-------------------------|------------|
| Install dependencies    | `uv sync`  |
| Execute unit tests      | `pytest .` |
| Format python code      | `black .`  |
| Verify type correctness | `mypy .`   |

## Adding Terminal Commands as Runnable IDE Tasks
We cannot easily ship IDE configuration files, meaning users will need to add run configurations on their own.

![Here's a video of me adding a configuration which runs our unit tests](https://github.com/user-attachments/assets/26bb134e-0b00-4700-aaf6-ee8d620fcd08).

In summary:
* Select the combo box in the top right next to the "run" and "debug" options, and select `Edit Configurations...`
* Add a new `Python` configuration
* Change from the type combo bow from `script` to `module`
* From the terminal commands table above, copy the first space-separated word into the `module` field
* Copy all remaining text from the command column into the `script parameters` field
* Set the `working directory` field to `$ContentRoot$`, either by typing it in or using the `Insert Macros...` button

## Enable Auto-Formatting on Save
* In PyCharm's settings, search for "Actions on save". It will be nested under the "Tools" heading
* Select "Run Black"
  * If there is a warning icon next to "Run Black", select the "configure..." option and
  * Set the interpreter field
  * Check "On code reformat" and "On save"
  
Now, any time you trigger a save through the IDE, the file will be reformatted appropriately.