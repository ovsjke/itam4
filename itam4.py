from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from string import ascii_letters,digits
from random import choices, randint
import uvicorn
from loguru import logger
import time
#commit
#Заранее извините, за этот ужас в коде, с трешовой 'архитектурой'
#Мне просто хотелось самому разобраться и с нуля написать проект этот,
#не просто копируя код с урока
links:dict[str,str] = {} #хранение ссылок
app = FastAPI()
class LinkRequest(BaseModel):
    original_link: str
class LinkResponce(BaseModel):
    short_link: str


class UnicornExcept(Exception): #класс для отлова ошибок
    def __init__(self, post: str, exception: Exception, method: str, status: int) :
        self.post = post
        self.exception = exception
        self.method = method
        self.status = status
        
@app.exception_handler(UnicornExcept) #метод для отлова и логирования ошибок
async def unicorn_exception_handler(request: Request, exc: UnicornExcept):
    logger.error(f"Произошла ошибка! запрос: {exc.method} {request.url}, ошибка: {exc.exception}")
    return JSONResponse(status_code = exc.status, content=
        f"url{request.url}, {exc.exception}"
    )
def create_shor_link(lenght: int) -> str: #метод для создания ссылки короткой
    all_symbols = ascii_letters+digits
    return ''.join(choices(all_symbols, k = lenght))
@app.middleware("http") #мидлварь
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()