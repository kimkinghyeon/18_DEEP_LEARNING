from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from routers import translate  

app = FastAPI()

# HTML 파일을 제공하기 위해 static 폴더를 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# 기본 라우트 설정: HTML 파일로 리다이렉트
@app.get("/")
async def read_root():
    return {"message": "Hello, please visit /static/index.html"}

# translate 라우터를 포함합니다.
app.include_router(translate.router)
