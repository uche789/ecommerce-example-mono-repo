from fastapi import Depends, FastAPI, File, HTTPException, Response, UploadFile, Request, Response
from contextlib import asynccontextmanager
from dbsetup import DataModel;
from fastapi.staticfiles import StaticFiles

dm = DataModel()

@asynccontextmanager
async def lifespan(app: FastAPI):
    dm.create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get('/products')
def get_app():
    data = {
        'name': 'this is a neme'
    }
    return data

# @app.post('/products')