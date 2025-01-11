from fastapi import FastAPI
from pixel_chunk.spa_static_files import SPAStaticFiles
from pixel_chunk.project import project_router


app = FastAPI()
app.include_router(project_router)
app.mount("/", SPAStaticFiles(directory="./frontend/dist/", html=True), name="app")
