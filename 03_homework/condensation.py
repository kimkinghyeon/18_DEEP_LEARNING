from transformers import pipeline
import requests

token = ""

# 요약 파이프라인 정의
pipe = pipeline("summarization", model="facebook/bart-large-cnn")

# API 설정
API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
headers = {"Authorization": f"Bearer {token}"}

# 쿼리 함수 정의
def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()

# 요약할 텍스트 입력 (길이를 줄여봅니다)
output = query({
    "inputs": "The Eiffel Tower is a wrought-iron lattice tower in Paris, France. It is 324 metres tall and was the tallest man-made structure for 41 years.",
})

# 출력 결과 확인
print("Summary Output:", output)

# 번역 파이프라인 정의
translator = pipeline(
    'translation',
    model='facebook/nllb-200-distilled-600M',
    device=-1,  # CPU에서 실행
    src_lang='eng_Latn',
    tgt_lang='kor_Hang',
    max_length=512
)


# 번역할 텍스트 설정
text_to_translate = output[0]['summary_text'] if isinstance(output, list) and len(output) > 0 else ""

# 번역 수행 (max_length 조정)
translated_text = translator(text_to_translate, max_length=256)[0]['translation_text'] if text_to_translate else "No text to translate."
print("Translated Text:", translated_text)

import re
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import nltk

# NLTK에서 punkt 다운로드 (이미 설치되어 있을 경우 건너뛰기)
nltk.download('punkt')

# 데이터 경로 확인
print(nltk.data.path)  # 데이터 경로 출력

# 모델 및 토크나이저 로드
model = AutoModelForSeq2SeqLM.from_pretrained('eenzeenee/t5-base-korean-summarization')
tokenizer = AutoTokenizer.from_pretrained('eenzeenee/t5-base-korean-summarization')

prefix = "summarize: "
sample = """
    안녕하세요? 우리 (2학년)/(이 학년) 친구들 우리 친구들 학교에 가서 진짜 (2학년)/(이 학년) 이 되고 싶었는데 학교에 못 가고 있어서 답답하죠? 
    그래도 우리 친구들의 안전과 건강이 최우선이니까요 오늘부터 선생님이랑 매일 매일 국어 여행을 떠나보도록 해요. 
    어/ 시간이 벌써 이렇게 됐나요? 늦었어요. 늦었어요. 빨리 국어 여행을 떠나야 돼요. 
    그런데 어/ 국어여행을 떠나기 전에 우리가 준비물을 챙겨야 되겠죠? 국어 여행을 떠날 준비물, 교안을 어떻게 받을 수 있는지 선생님이 설명을 해줄게요. 
    (EBS)/(이비에스) 초등을 검색해서 들어가면요 첫화면이 이렇게 나와요. 
    자/ 그러면요 여기 (X)/(엑스) 눌러주(고요)/(구요). 저기 (동그라미)/(똥그라미) (EBS)/(이비에스) (2주)/(이 주) 라이브특강이라고 되어있죠? 
    거기를 바로 가기를 누릅니다. 자/ (누르면요)/(눌르면요). 어떻게 되냐? b/ 밑으로 내려요 내려요 내려요 쭉 내려요. 
    우리 몇 학년이죠? 아/ (2학년)/(이 학년) 이죠 (2학년)/(이 학년)의 무슨 과목? 국어. 
    이번주는 (1주)/(일 주) 차니까요 여기 교안. 다음주는 여기서 다운을 받으면 돼요. 
    이 교안을 클릭을 하면, 짜잔/. 이렇게 교재가 나옵니다 .이 교안을 (다운)/(따운)받아서 우리 국어여행을 떠날 수가 있어요. 
    그럼 우리 진짜로 국어 여행을 한번 떠나보도록 해요? 국어여행 출발. 자/ (1단원)/(일 단원) 제목이 뭔가요? 한번 찾아봐요. 
    시를 즐겨요 에요. 그냥 시를 읽어요 가 아니에요. 시를 즐겨야 돼요 즐겨야 돼. 어떻게 즐길까? 일단은 내내 시를 즐기는 방법에 대해서 공부를 할 건데요. 
    그럼 오늘은요 어떻게 즐길까요? 오늘 공부할 내용은요 시를 여러 가지 방법으로 읽기를 공부할겁니다. 
    어떻게 여러가지 방법으로 읽을까 우리 공부해 보도록 해요. 오늘의 시 나와라 짜잔/! 시가 나왔습니다 시의 제목이 뭔가요? 다툰 날이에요 다툰 날. 
    누구랑 다퉜나 동생이랑 다퉜나 언니랑 친구랑? 누구랑 다퉜는지 선생님이 시를 읽어 줄 테니까 한번 생각을 해보도록 해요."""

inputs = [prefix + sample]

# 텍스트 토큰화
inputs = tokenizer(inputs, max_length=512, truncation=True, return_tensors="pt")

# 요약 생성
output = model.generate(**inputs, num_beams=3, do_sample=True, min_length=10, max_length=64)

# 디코딩
decoded_output = tokenizer.batch_decode(output, skip_special_tokens=True)[0]

# 문장 분리 및 첫 문장 출력 (정규 표현식 사용)
result = re.split(r'(?<=[.!?]) +', decoded_output.strip())[0]  # 문장을 기준으로 분리
print('RESULT >>', result)