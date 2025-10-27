.PHONY: install install-dev lint test clean run help

help:
	@echo "Available targets:"
	@echo "  make install     - Install package in editable mode"
	@echo "  make install-dev - Install with development dependencies"
	@echo "  make lint        - Run linters (ruff, mypy)"
	@echo "  make test        - Run pytest with coverage"
	@echo "  make clean        - Clean build artifacts"
	@echo "  make run          - Example usage (requires API keys)"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"

lint:
	ruff check src/ tests/
	mypy src/

test:
	pytest tests/ --cov=hybrid_pdf_parser --cov-report=html --cov-report=term

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache/
	rm -rf .ruff_cache/
	rm -rf htmlcov/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

run:
	@echo "Example: Edit run_example.py with your PDF and API keys"
	python -c "from hybrid_pdf_parser import PDFExtractor; print('Package installed successfully')"

demo:
	@echo "Opening Jupyter notebook demo..."
	jupyter notebook demo.ipynb

