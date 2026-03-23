# Backend - Python Physics Engine & FastAPI

Core Python engine for the Precision with Light photonics platform.

## Structure

- `core/1_Intent_Layer/` - RAG, LLM Parsers, Pydantic Schemas
- `core/2_generative_engine/` - PyTorch AI Models
- `core/3_simulation_bridge/` - Solver Automations (Lumerical/COMSOL)
- `core/4_fabrication_export/` - GDSII & STL mask generation
- `api/` - FastAPI Gateway endpoints
- `data/` - Data generation scripts

## Requirements

See `../requirements.txt` for Python dependencies.
