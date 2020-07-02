bash:
	docker exec -it djangoplicity-customsearch bash

test:
	docker exec -it djangoplicity-customsearch coverage run --source='.' manage.py test

coverage-html:
	docker exec -it djangoplicity-customsearch coverage html
	open ./htmlcov/index.html

test-python27:
	docker exec -it djangoplicity-customsearch tox -e py27-django111
