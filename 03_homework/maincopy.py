from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from transformers import pipeline
from pydantic import BaseModel
import httpx
import torch
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import re
import os

app = FastAPI()

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 필요시 도메인 변경
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTML 파일을 제공하기 위해 static 폴더를 설정
app.mount("/static", StaticFiles(directory="static"), name="static")

# API 설정
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
token = "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"  # 자신의 토큰으로 변경하세요
headers = {"Authorization": f"Bearer {token}"}

async def query(payload):
    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()

# 요약 및 번역 파이프라인 정의
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
translator = pipeline(
    'translation',
    model='facebook/nllb-200-distilled-600M',
    device=-1,
    src_lang='eng_Latn',
    tgt_lang='kor_Hang',
    max_length=512
)

class TextInput(BaseModel):
    text: str  # text라는 속성을 가진 모델 정의

@app.post("/en-summarize/")
async def summarize(input: TextInput):  # TextInput 타입을 사용하여 요청 본문을 처리
    text = input.text  # input.text로 전달된 값을 사용
    if not text:
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")
    
    # 요약 요청
    output = await query({"inputs": text})
    summary_text = output[0]['summary_text'] if isinstance(output, list) and len(output) > 0 else ""
    translated_text = translator(summary_text, max_length=256)[0]['translation_text'] if summary_text else "No text to translate."
    return {"summary": summary_text, "translated_summary": translated_text}

# 한국어 요약을 위한 모델 및 토크나이저 로드
model_name = 'eenzeenee/t5-base-korean-summarization'
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

prefix = "summarize: "

@app.post("/kr-summarize/")
async def kr_summarize(input: TextInput):  # Pydantic 모델 사용
    text = input.text.strip()  # 입력 텍스트 전처리
    if not text:
        raise HTTPException(status_code=400, detail="Input text cannot be empty.")

    inputs = [prefix + text]  # 요약 요청을 위한 prefix 추가

    # 텍스트 토큰화
    tokenized_inputs = tokenizer(inputs, max_length=512, truncation=True, return_tensors="pt")

    # 요약 생성
    with torch.no_grad():  # 메모리 절약을 위해 gradient 계산 비활성화
        output = model.generate(**tokenized_inputs, num_beams=3, do_sample=True, min_length=10, max_length=64)

    # 디코딩
    decoded_output = tokenizer.batch_decode(output, skip_special_tokens=True)[0]

    # 문장 분리 및 첫 문장 출력
    result = re.split(r'(?<=[.!?]) +', decoded_output.strip())[0]  # 문장을 기준으로 분리
    return {"summary": result}

# 기본 라우트 설정: HTML 파일로 리다이렉트
@app.get("/")
async def read_root():
    return {"message": "Hello, please visit /static/index.html"}
