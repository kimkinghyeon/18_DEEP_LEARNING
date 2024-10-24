import re
import torch
from fastapi import HTTPException
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM, pipeline
import httpx

# 영어 요약 및 번역을 위한 Hugging Face API 설정
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
token = ""  # 자신의 토큰으로 변경하세요
headers = {"Authorization": f"Bearer {token}"}

translator = pipeline(
    'translation',
    model='facebook/nllb-200-distilled-600M',
    device=-1,
    src_lang='eng_Latn',
    tgt_lang='kor_Hang',
    max_length=256
)

# 한국어 요약을 위한 모델 및 토크나이저 로드
model_name = 'eenzeenee/t5-base-korean-summarization'
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
tokenizer = AutoTokenizer.from_pretrained(model_name)

prefix = "summarize: "

async def query_huggingface_api(payload):
    async with httpx.AsyncClient() as client:
        response = await client.post(API_URL, headers=headers, json=payload, timeout=10.0)  # 10초 타임아웃
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.json())
    return response.json()

async def summarize_text(text: str):
    """영어 텍스트를 요약하고 번역하는 함수."""
    output = await query_huggingface_api({"inputs": text})
    summary_text = output[0]['summary_text'] if isinstance(output, list) and len(output) > 0 else ""
    translated_text = translator(summary_text, max_length=256)[0]['translation_text'] if summary_text else "No text to translate."
    return {"summary": summary_text, "translated_summary": translated_text}

async def kr_summarize_text(text: str):
    """한국어 텍스트를 요약하는 함수."""
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
