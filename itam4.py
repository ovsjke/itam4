from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from string import ascii_letters,digits
from random import choices, randint
import uvicorn
from loguru import logger
import time
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
class UnicornExcept(Exception): #класс для отлова ошибок.
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
    response = await call_next(request)
    process_time = round((time.perf_counter() - start_time)*1000,2)
    response.headers["X-Lanetcy"] = str(process_time)
    logger.debug("{} {} done is {}ms", request.method, request.url, process_time)
    return response
@app.post("/shorten")
def post_link(link_requests: LinkRequest) -> LinkResponce:
    try:
        url = link_requests.original_link
        if not url.startswith(('http://', 'https://')): 
            url = "https://"+url
        if '.' not in url or ' ' in url:
            raise HTTPException(status_code= status.HTTP_422_UNPROCESSABLE_CONTENT, detail= "Url not validate")
        short_url = create_shor_link(randint(4,8))
        links[short_url] = url
        return LinkResponce(short_link=f"http://127.0.0.1:8000/{short_url}")
    except Exception as e:
        raise UnicornExcept(post = link_requests.original_link, exception = e, method = 'post',status = status.HTTP_400_BAD_REQUEST)
@app.get("/{url}")
def redirect(url: str):
    try:
        if url not in links:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail = "Link not found")
        return RedirectResponse(links[url])
    except Exception as e:
        raise UnicornExcept(post = url, exception = e, method = 'get',status = status.HTTP_404_NOT_FOUND)
uvicorn.run(app)