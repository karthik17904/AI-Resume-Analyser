from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from app.api.routes import analysis, studio, chat, pdf_templates

app=FastAPI(title='AI Resume Analyser',version='4.1.0',description='Explainable local analysis with optional reviewed AI rewriting.')
app.add_middleware(CORSMiddleware,allow_origins=['http://localhost:5173','http://127.0.0.1:5173'],allow_credentials=False,allow_methods=['GET','POST','DELETE'],allow_headers=['*'])
app.include_router(analysis.router)
app.include_router(studio.router)
app.include_router(chat.router)
app.include_router(pdf_templates.router)

@app.get('/api/health')
def health():return {'status':'ok','app':'AI Resume Analyser','version':'4.1.0'}

# In production, serve Vite's compiled assets from FastAPI. In development, use the Vite dev server.
DIST=Path(__file__).resolve().parents[2]/'frontend'/'dist'
if DIST.exists():
    app.mount('/assets',StaticFiles(directory=DIST/'assets'),name='assets')
    @app.get('/')
    def root():return FileResponse(DIST/'index.html')
    @app.get('/{full_path:path}')
    def spa(full_path:str):
        if full_path.startswith('api/') or full_path.startswith('assets/'):return {'detail':'Not found'}
        return FileResponse(DIST/'index.html')
