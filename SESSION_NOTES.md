## Session Notes

### Demo Runtime

- Run the demo with the repo virtualenv interpreter: `./.venv/bin/python demo.py`
- `python` was not available on PATH in this environment, but `python3` was.
- `langextract` is installed in the repo virtualenv at `.venv`.

### Ollama Setup

- `demo.py` is configured to use:
  - model: `phi3.5`
  - URL: `http://localhost:11434`
- `ollama` is installed at `/home/david/.local/bin/ollama`
- The local model `phi3.5:latest` was present.
- The Ollama server was not running by default and had to be started with `ollama serve`.
- Ollama was stopped again after testing.

### Last Observed Failure

- The demo started successfully once Ollama was running, but extraction failed after inference.
- Observed error:

```text
ERROR:absl:Extraction text must be a string, integer, or float. Found: <class 'dict'>
ValueError: Extraction text must be a string, integer, or float.
```

- This suggests the model response shape from `phi3.5` did not match what `langextract` expected for the current prompt/example setup in `demo.py`.

### Notes About `demo.py`

- The currently active input text in `demo.py` is:

```text
Laboratory testing of soils collected at the boring locations revealed the near-surface soil possesses "low" expansion potential when testing in accordance with the ASTM International D4829 test method (Figures A1 and A2).
```

- There is also a commented-out alternate text block about test borings and CPT soundings that may be a better fit for the current extraction prompt/examples.
