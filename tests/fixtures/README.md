# Test Fixtures

This directory contains PDF files used for integration testing.

## Adding Test PDFs

1. Add your PDF file here (e.g., `sample_brochure.pdf`)
2. Update `test_pipeline_integration.py` to reference it
3. Files are ignored by `.gitignore` to avoid committing large binaries

## Running Integration Tests

Integration tests are skipped by default. To run them:

1. Remove or comment out the `@pytest.mark.skip` decorator in `tests/test_pipeline_integration.py`
2. Ensure you have a valid `OPENAI_API_KEY` in your environment
3. Add test PDF files to this directory
4. Run tests:
   ```bash
   pytest tests/test_pipeline_integration.py -v
   ```

Or mark tests with a custom marker and run with:
```bash
pytest -m integration  # Run integration tests only
pytest -m "not integration"  # Skip integration tests
```

