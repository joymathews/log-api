from google.oauth2 import id_token
from google.auth.transport import requests
from fastapi import FastAPI, HTTPException, Depends, Header
from log_table import LogTable
from dotenv import load_dotenv
import os
from mangum import Mangum
load_dotenv()
app = FastAPI()
print("DAte")
def validate_google_token(token: str):
    try:
        CLIENT_ID = os.getenv("CLIENT_ID")
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_ID)
        user_id = idinfo['email']
        return user_id
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid Google OAuth token")

def get_current_user(authorization: str = Header(...)):
    token = authorization.split(" ")[1]
    return validate_google_token(token)

@app.get("/")
async def root():
    return {"message": "Welocme to the log API"}

@app.post("/v1/weight")
async def add_weight(weight: float, user_name=Depends(get_current_user)):
    log = LogTable()
    response = log.AddWeight(user_name, weight)
    if not response:
        raise HTTPException(status_code=404, detail="Could not log weight")
    return {"weight": weight}

@app.get("/v1/weight")
async def get_weight(user_name=Depends(get_current_user)):
    log = LogTable()
    return log.GetWeight(user_name)

handler = Mangum(app=app)