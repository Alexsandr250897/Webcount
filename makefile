PYTHON_FILE = count_word.py
run:
	python $(PYTHON_FILE)

typecheck:
	mypy $(PYTHON_FILE)
