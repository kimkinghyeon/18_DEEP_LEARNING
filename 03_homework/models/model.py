from pydantic import BaseModel

class TextInput(BaseModel):
    text: str  # text라는 속성을 가진 모델 정의