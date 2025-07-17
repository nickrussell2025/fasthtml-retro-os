fix:
	uv run ruff check --fix .
	uv run ruff format .

test:
	uv run pytest

dev:
	uv run python main.py

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete