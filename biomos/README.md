# GBIF Package

#### Install Python Dependency Manager

Refer : https://python-poetry.org/docs/


#### Install Local Dependencies
This should create a local env variable and install all the libs
```
cd gbif
poetry install
```
![image](https://user-images.githubusercontent.com/65660549/179351282-ec1c04d5-eb6f-41e5-b2a7-72b82e7689ab.png)


#### Build Package
This should create *tar or *whl for us to invoke in any application under ```dist``` directory 
```
poetry build
```
![image](https://user-images.githubusercontent.com/65660549/179351304-744af1a2-5e9f-45e3-bd20-9e58a9647abb.png)


#### Test Package
Local Test of the package
```
poetry run pytest
```
![image](https://user-images.githubusercontent.com/65660549/179351333-e04b4352-876b-4901-bb26-76e3381e8ed6.png)

#### Package Functions
- GBIF Occurences
- Climate Covariates
- Soil Composition Covariates
- Human Interference 
- Land Cover Types



#### Package Usage
Refer to ```tests/test_biomos.py```  for usage

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