from fastapi import FastAPI, Request, Depends, HTTPException, status, Cookie, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Annotated

app = FastAPI()
templates = Jinja2Templates(directory="templates")


db_usuarios = []


class Usuario(BaseModel):
    nome: str
    senha: str
    bio: str

class LoginRequest(BaseModel):
    nome: str
    senha: str


def get_usuario_logado(session_user: Annotated[str | None, Cookie()] = None):
    if not session_user:
        raise HTTPException(status_code=401, detail="Não logado")
    

    for u in db_usuarios:
        if u["nome"] == session_user:
            return u
    raise HTTPException(status_code=401, detail="Sessão inválida")


@app.get("/", response_class=HTMLResponse)
def pg_registro(request: Request):

    return templates.TemplateResponse(request=request, name="index.html")

@app.get("/login", response_class=HTMLResponse)
def pg_login(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/home", response_class=HTMLResponse)
def pg_perfil(request: Request, user: dict = Depends(get_usuario_logado)):

    return templates.TemplateResponse(
        request=request, 
        name="perfil.html", 
        context={"nome": user["nome"], "bio": user["bio"]}
    )

@app.get("/login", response_class=HTMLResponse)
def pg_login(request: Request):

    return templates.TemplateResponse(request=request, name="login.html")

@app.get("/home", response_class=HTMLResponse)
def pg_perfil(request: Request, user: dict = Depends(get_usuario_logado)):

    return templates.TemplateResponse(
        request=request, 
        name="perfil.html", 
        context={"nome": user["nome"], "bio": user["bio"]}
    )



@app.post("/users")
def criar_usuario(user: Usuario):

    db_usuarios.append(user.dict())
    return {"message": f"Usuário {user.nome} criado!"}

@app.post("/login")
def login(dados: LoginRequest, response: Response):
    for u in db_usuarios:
        if u["nome"] == dados.nome and u["senha"] == dados.senha:
            response.set_cookie(key="session_user", value=dados.nome)
            return {"status": "ok"}
    raise HTTPException(status_code=404, detail="Usuário ou senha incorretos")