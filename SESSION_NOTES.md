## Session Notes

### Current Setup

- The demo now uses OpenAI via `OPENAI_API_KEY` loaded from `.env`.
- Current model in `demo.py`: `gpt-4.1-mini`
- The project is managed with `uv`.
- Primary run command: `uv run python demo.py`

### Project Files

- `demo.py`: LangExtract demo with:
  - few-shot positive examples
  - few-shot negative examples
  - positive test texts
  - negative test texts
  - Pydantic post-processing into normalized boring records
- `pyproject.toml`: minimal `uv` project config
- `uv.lock`: locked dependency graph
- `.gitignore`: ignores `.env`, `.venv`, and `__pycache__`

### Demo Behavior

- `langextract` is being used as a thin orchestration layer around the LLM:
  - builds the prompt from `prompt` + `examples`
  - sends it to the model
  - parses output into flat `Extraction` objects
- `demo.py` then groups those flat extractions into record-like objects with Pydantic.

### Pydantic Normalization

- `BoringRecord` normalizes extracted values after `langextract` returns them.
- `number_of_borings` is converted from values like `one`, `two`, `eight` into integers.
- `min_depth` and `max_depth` are normalized to floats.

### Prompt / Example Notes

- The examples were cleaned up to align more literally with their source text.
- Remaining prompt-alignment warnings are mostly due to LangExtract’s strict span matching on short values like:
  - `Two`
  - `8`
  - `50`
  - `100`
- Negative examples with `extractions=[]` caused LangExtract prompt validation to fail, so:
  - `prompt_validation_level` is set to `OFF` in the demo

### Model Findings

- `phi3.5` via Ollama was highly non-deterministic and often produced malformed structured output.
- Restarting Ollama sometimes changed behavior, confirming instability.
- `gpt-4.1-mini` behaved much more reliably for this extraction task.

### Negative Coverage

- The prompt now includes negative examples that should produce no extraction output.
- The demo also runs separate negative test texts that are different from the negative prompt examples.
- Current negative test behavior is good: no extractions, no normalized records.

### Git / Repo

- Local git history includes incremental commits for:
  - extraction refactor
  - multiple sample texts
  - prompt printing
  - OpenAI model switch
  - example cleanup
  - `uv` project setup
  - Pydantic normalization
  - negative examples and test texts
- Repo was pushed to:
  - `https://github.com/macterra/langextract-demo`

### Useful Commands

- Run demo: `uv run python demo.py`
- Sync environment: `uv sync`
- Show remotes: `git remote -v`
