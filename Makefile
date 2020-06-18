bash:
	docker exec -it djangoplicity-customsearch-web bash

test:
	docker exec -it djangoplicity-customsearch-web coverage run --source='.' manage.py test

coverage-html:
	docker exec -it djangoplicity-customsearch-web coverage html
	open ./htmlcov/index.html

test-python27:
	docker exec -it djangoplicity-customsearch-web tox -e py27-django111