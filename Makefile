flake:
	flake8

black:
	black -S gravyvalet charon

isort:
	isort .

lintall: black isort flake
