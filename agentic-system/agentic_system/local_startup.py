import os

import uvicorn
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv(os.path.join(".env"))
    uvicorn.run("agentic_system.main:app", host="0.0.0.0", port=5051, reload=True)
