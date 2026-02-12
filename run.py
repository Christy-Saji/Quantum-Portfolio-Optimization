import sys
from pathlib import Path

backend_dir = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_dir))

from api import app
import uvicorn

if __name__ == "__main__":
    print("=" * 50)
    print("Quantum Portfolio Optimizer")
    print(f"API: http://localhost:8000 | Docs: http://localhost:8000/docs")
    print("=" * 50)
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
