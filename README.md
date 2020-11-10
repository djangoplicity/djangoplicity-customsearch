# Djangoplicity Customsearch

![Coverage](https://img.shields.io/codecov/c/github/djangoplicity/djangoplicity-customsearch/develop)
![Size](https://img.shields.io/github/repo-size/djangoplicity/djangoplicity-customsearch)
![License](https://img.shields.io/github/license/djangoplicity/djangoplicity-customsearch)
![Language](https://img.shields.io/github/languages/top/djangoplicity/djangoplicity-customsearch)

Djangoplicity Customsearch is a dependency of the [Djangoplicity](https://github.com/djangoplicity/djangoplicity) CMS
created by the European Southern Observatory (ESO) for managing internal searches.

* [Requirements](#requirements)
* [Installation](#installation)
* [Development](#development)
    * [Cloning the repository](#cloning-the-repository)
    * [Running the project](#running-the-project)
* [License](#license)

## Installation
Djangoplicity Customsearch currently supports Python 2.7 and Python 3+.

You must install Djangoplicity Customsearch using the Github repository, so add the following packages to your
requirements depending on the Python version you are using.
```
# For Python 3+
git+https://@github.com/djangoplicity/djangoplicity.git@release/python3

git+https://@github.com/djangoplicity/djangoplicity-customsearch.git@release/python3

# For Python 2.7
git+https://@github.com/djangoplicity/djangoplicity.git@develop

git+https://@github.com/djangoplicity/djangoplicity-customsearch.git@develop

# Asynchronous Task Queue
celery==4.4.7
```
Celery is also required for some asynchronous tasks to work.

Now include the package in your [INSTALLED_APPS](test_project/settings.py#L31).

Djangoplicity requires some additional settings in order to work, so add [this](test_project/settings.py#L139) configuration to your settings
file (you don't have to include those files in your assets).

You can find more information about the required code in the [test_project](test_project) folder.

## Development

This repository includes an example project for local development located in the test_project folder. You can find
there the basic configuration to get a project working.
 
### Cloning the repository

In your terminal run the command:

```` 
git clone https://gitlab.com/djangoplicity/djangoplicity-customsearch.git
````

### Running the project

All the configuration to start the project is present in the docker-compose files and Dockerfile,
then at this point a single command is required to download all the dependencies and run the project:

```` 
docker-compose up
````

> The previous command reads the config from docker-compose.yml. 

When the process finishes, the server will be available at *`localhost:8002`*

To stop containers press `CTRL + C` in Windows or `⌘ + C` in MacOS

If the dependencies change, you should recreate the docker images and start the containers again with this command:

```` 
docker-compose up --build
````

### Additional commands

Inside the `Makefile` there are multiple command shortcuts, they can be run in UNIX systems like this:

```
make <command-name>
```

E.g.

```
make test
```

> In Windows you can just copy and paste the related command

## License

This repository is released under the [GPL-2.0 License](LICENSE)
