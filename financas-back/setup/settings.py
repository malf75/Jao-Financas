import os
from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(override=True)
app = FastAPI()

KEY = os.getenv('KEY')
SECRET_KEY = str(os.getenv('SECRET_KEY'))
DATABASE_URL = str(os.getenv('DATABASE_URL'))
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_HOURS = 360

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)