from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()


templates = Jinja2Templates(directory="templates")
estado = {"curtidas": 0}

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):

    return templates.TemplateResponse(
        request=request, 
        name="index.html", 
        context={"curtidas": estado["curtidas"]}
    )

@app.post("/curtir", response_class=HTMLResponse)
async def curtir(request: Request):
    estado["curtidas"] += 1
    return templates.TemplateResponse(
        request=request, 
        name="partials/contador.html", 
        context={"curtidas": estado["curtidas"]}
    )

@app.post("/zerar", response_class=HTMLResponse) 
async def limpar_curtidas(request: Request):
    estado["curtidas"] = 0
    return templates.TemplateResponse(
        request=request, 
        name="partials/contador.html", 
        context={"curtidas": estado["curtidas"]}
    )

# Rotas das Abas
@app.get("/aba-curtidas", response_class=HTMLResponse)
async def aba_curtidas(request: Request):
    return templates.TemplateResponse(
        request=request, 
        name="partials/aba_curtidas.html", 
        context={"curtidas": estado["curtidas"]}
    )

@app.get("/aba-jupiter", response_class=HTMLResponse)
async def aba_jupiter(request: Request):
    # Renderiza o novo arquivo que criaremos na pasta partials
    return templates.TemplateResponse(
        request=request, 
        name="partials/aba_jupiter.html"
    )

@app.get("/aba-professor", response_class=HTMLResponse)
async def aba_professor(request: Request):
    return HTMLResponse("Em construcao")