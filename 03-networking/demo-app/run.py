import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host="0.0.0.0", #  tells FastAPI/Uvicorn to accept connections from other devices on your network.
        port=8000,
        reload=True
    )
