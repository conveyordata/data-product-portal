import uvicorn

if __name__ == "__main__":
    uvicorn.run("agentic_system.main:app", host="0.0.0.0", port=5051, reload=True)
