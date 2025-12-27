from fastapi import FastAPI
from auth import router
from admin import router as re
from student import router as r

app=FastAPI()
app.include_router(router)
app.include_router(re)
app.include_router(r)