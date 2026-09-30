#!/usr/bin/env bash
# Start KrishiMitra AI locally:  ./run.sh   (optional: PORT=8502 ./run.sh)
cd "$(dirname "$0")"
export USE_TF=0 USE_FLAX=0
exec streamlit run app/app.py --server.port "${PORT:-8501}" "$@"
