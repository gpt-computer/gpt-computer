## Latest Changes

* **Project Restructure (v0.3.0)**: Consolidated dual-package structure (`gpt_computer` + `gptc`) into a single, well-organized package with clear module boundaries. All legacy imports continue to work with deprecation warnings. See `MIGRATION_GUIDE.md` for details.
* **New module layout**: `ai/`, `agent/`, `execution/`, `interfaces/`, `analysis/`, `infrastructure/` replace the old flat `core/` directory.
* **Compatibility shims**: All old import paths (`gptc.*`, `gpt_computer.core.*`) continue to work with `DeprecationWarning`.
* **Static import analysis**: New `tests/test_static_imports.py` validates no import cycles and correct dependency directions.
* Add new repository intelligence and context OS modules. PR [#65](https://github.com/gpt-computer/gpt-computer/pull/65) by [@khulnasoft-research](https://github.com/khulnasoft-research).
* Update authors and repository information in pyproject.toml. PR [#66](https://github.com/gpt-computer/gpt-computer/pull/66) by [@FortiShield](https://github.com/FortiShield).
