# GBIF Package

#### Install Python Dependency Manager

Refer : https://python-poetry.org/docs/


#### Install Local Dependencies
This should create a local env variable and install all the libs
```
poetry install
```

#### Build Package
This should create *tar or *whl for us to invoke in any application under ```dist``` directory 
```
poetry build
```

#### Test Package
Local Test of the package
```
poetry run pytest
```

#### Using the poetry env to use for Jupyter
Get the env variable name
```
poetry env info
```
- Use this variable for your py-kernel when you launch your jupyter instance in vscode. 
- If you cant find this, then:
- Ctrl/Cmd + P
- Select Python Interpreter
- Enter Interpreter Path
- Use the path as per ```poetry env info``` to add your ``venv`` to vs code

#### Writing your function
TBC
