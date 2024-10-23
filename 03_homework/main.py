from fastapi import FastAPI, HTTPException
from transformers import pipeline
import requests
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import re
# import nltk : nltk 설치가 필요할때 사용 [이미 다운받아서 건너뛰기]

app = FastAPI()

# API 설정
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
token = ""  # 자신의 토큰으로 변경하세요
headers = {"Authorization": f"Bearer {token}"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()

# 요약 파이프라인 정의
summarizer = pipeline("summarization", model="facebook/bart-large-cnn")

# 번역 파이프라인 정의
translator = pipeline(
    'translation',
    model='facebook/nllb-200-distilled-600M',
    device=-1,  # CPU에서 실행
    src_lang='eng_Latn',
    tgt_lang='kor_Hang',
    max_length=512
)

@app.post("/en-summarize/")
async def summarize(text: str):
    # 요약 요청
    output = query({"inputs": text})
    summary_text = output[0]['summary_text'] if isinstance(output, list) and len(output) > 0 else ""

    # 번역 요청
    translated_text = translator(summary_text, max_length=256)[0]['translation_text'] if summary_text else "No text to translate."

    return {"summary": summary_text, "translated_summary": translated_text}

# 한국어 요약을 위한 모델 및 토크나이저 로드
model_name = 'eenzeenee/t5-base-korean-summarization'
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

prefix = "summarize: "

@app.post("/kr-summarize/")
async def kr_summarize(text: str):
    # 입력 텍스트 전처리
    inputs = [prefix + text]

    # 텍스트 토큰화
    tokenized_inputs = tokenizer(inputs, max_length=512, truncation=True, return_tensors="pt")

    # 요약 생성
    output = model.generate(**tokenized_inputs, num_beams=3, do_sample=True, min_length=10, max_length=64)

    # 디코딩
    decoded_output = tokenizer.batch_decode(output, skip_special_tokens=True)[0]

    # 문장 분리 및 첫 문장 출력
    result = re.split(r'(?<=[.!?]) +', decoded_output.strip())[0]  # 문장을 기준으로 분리
    return {"summary": result}
