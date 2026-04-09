import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form, Depends, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from typing import Optional

from database import engine, create_db_and_tables, get_session
from models import Player, MonkeyUpgrade, PlayerUpgrade

@asynccontextmanager
async def lifespan(app: FastAPI):

    create_db_and_tables()
    with Session(engine) as session:
        upgrades = session.exec(select(MonkeyUpgrade)).all()
        correct_data = {
            "Macaco Prego": {"cost": 15, "bps": 1, "image": "🐒", "type": "monkey"},
            "Mico Leão Dourado": {"cost": 100, "bps": 5, "image": "🦁", "type": "monkey"},
            "Orangotango": {"cost": 250, "bps": 10, "image": "🦧", "type": "monkey"},
            "Gorila": {"cost": 500, "bps": 20, "image": "🦍", "type": "monkey"},
            "Martelo": {"cost": 150, "bps": 0, "image": "🔨", "type": "boost", "target": "Macaco Prego", "val": 2},
            "Super Juba": {"cost": 800, "bps": 0, "image": "👑", "type": "boost", "target": "Mico Leão Dourado", "val": 5},
            "Envergadura avantajada": {"cost": 2000, "bps": 0, "image": "💪", "type": "boost", "target": "Orangotango", "val": 12},
            "Supino de 1 tonelada": {"cost": 5000, "bps": 0, "image": "🏋️", "type": "boost", "target": "Gorila", "val": 20}
        }
        
        if not upgrades:
            monkeys = [
                MonkeyUpgrade(name="Cursor Dourado", base_cost=50, bananas_per_second=0, image_url="🖱️", upgrade_type="click", boost_value=1),
                MonkeyUpgrade(name="Macaco Prego", base_cost=15, bananas_per_second=1, image_url="🐒", upgrade_type="monkey"),
                MonkeyUpgrade(name="Mico Leão Dourado", base_cost=100, bananas_per_second=5, image_url="🦁", upgrade_type="monkey"),
                MonkeyUpgrade(name="Orangotango", base_cost=250, bananas_per_second=10, image_url="🦧", upgrade_type="monkey"),
                MonkeyUpgrade(name="Gorila", base_cost=500, bananas_per_second=20, image_url="🦍", upgrade_type="monkey"),
                MonkeyUpgrade(name="Martelo", base_cost=150, bananas_per_second=0, image_url="🔨", upgrade_type="boost", boost_target="Macaco Prego", boost_value=2),
                MonkeyUpgrade(name="Super Juba", base_cost=800, bananas_per_second=0, image_url="👑", upgrade_type="boost", boost_target="Mico Leão Dourado", boost_value=5),
                MonkeyUpgrade(name="Envergadura avantajada", base_cost=2000, bananas_per_second=0, image_url="💪", upgrade_type="boost", boost_target="Orangotango", boost_value=12),
                MonkeyUpgrade(name="Supino de 1 tonelada", base_cost=5000, bananas_per_second=0, image_url="🏋️", upgrade_type="boost", boost_target="Gorila", boost_value=20)
            ]
            session.add_all(monkeys)
            session.commit()
        else:
            for u in upgrades:
                if u.id == 4:
                    u.name = "Mico Leão Dourado"
                    u.base_cost = 100
                    u.bananas_per_second = 5
                    u.image_url = "🦁"
                elif u.id == 5:
                    u.name = "Orangotango"
                    u.base_cost = 250
                    u.bananas_per_second = 10
                    u.image_url = "🦧"
                elif u.id == 6:
                    u.name = "Gorila"
                    u.base_cost = 500
                    u.bananas_per_second = 20
                    u.image_url = "🦍"
                elif u.id == 3:
                    u.name = "Martelo"
                    u.base_cost = 150
                    u.image_url = "🔨"
                    u.boost_target = "Macaco Prego"
                elif u.id == 7:
                    u.name = "Super Juba"
                    u.base_cost = 800
                    u.image_url = "👑"
                    u.boost_target = "Mico Leão Dourado"
                    u.boost_value = 5
                elif u.id == 8:
                    u.name = "Envergadura avantajada"
                    u.base_cost = 2000
                    u.image_url = "💪"
                    u.boost_target = "Orangotango"
                    u.boost_value = 12
                elif u.id == 9:
                    u.name = "Supino de 1 tonelada"
                    u.base_cost = 5000
                    u.image_url = "🏋️"
                    u.boost_target = "Gorila"
                    u.boost_value = 20
            session.commit()
    yield


app = FastAPI(lifespan=lifespan)

os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
def index(request: Request, session: Session = Depends(get_session)):
    """Render the landing page for login/registration and top leaderboard."""
    top_players = session.exec(select(Player).order_by(Player.bananas_count.desc()).limit(10)).all() 
    return templates.TemplateResponse(request=request, name="index.html", context={"players": top_players})

@app.post("/register", response_class=HTMLResponse)
def register(request: Request, username: str = Form(...), session: Session = Depends(get_session)):
    """HTMX endpoint to create a new player or login existing one."""
    player = session.exec(select(Player).where(Player.username == username)).first()
    if not player:
        player = Player(username=username, bananas_count=0)
        session.add(player)
        session.commit()
        session.refresh(player)
    
    upgrades = session.exec(select(MonkeyUpgrade)).all()
    owned_rows = session.exec(select(PlayerUpgrade).where(PlayerUpgrade.player_id == player.id)).all()
    owned_upgrades = {row.upgrade_id: row.quantity for row in owned_rows}
    
    boosts = {}
    click_power = 1
    
    # Calcula modificadores
    for upg in upgrades:
        qty = owned_upgrades.get(upg.id, 0)
        if upg.upgrade_type == "boost" and upg.boost_target:
            boosts[upg.boost_target] = boosts.get(upg.boost_target, 0) + (upg.boost_value * qty)
        elif upg.upgrade_type == "click":
            click_power += (upg.boost_value * qty)
            
    # Calcula bananas por segundo
    bps = 0
    for upg in upgrades:
        if upg.upgrade_type == "monkey":
            qty = owned_upgrades.get(upg.id, 0)
            eff_bps = upg.bananas_per_second + boosts.get(upg.name, 0)
            bps += eff_bps * qty

    # Retorna template do jogo
    return templates.TemplateResponse(request=request, name="game.html", context={
        "player": player,
        "upgrades": upgrades,
        "owned_upgrades": owned_upgrades,
        "bps": bps,
        "click_power": click_power
    })

@app.put("/player/{player_id}/save", response_class=HTMLResponse)
def save_score(request: Request, player_id: int, bananas_count: int = Form(...), session: Session = Depends(get_session)):
    """HTMX endpoint to sync bananas count from the client periodically."""
    player = session.get(Player, player_id)
    if player:
        # Atualiza apenas se a nova contagem for maior
        if bananas_count > player.bananas_count:
            player.bananas_count = bananas_count
            session.add(player)
            session.commit()
            session.refresh(player)
    return HTMLResponse(content=f"Saved! (Total: {player.bananas_count})", status_code=200)

@app.post("/player/{player_id}/buy/{upgrade_id}", response_class=HTMLResponse)
def buy_upgrade(request: Request, player_id: int, upgrade_id: int, bananas_count: int = Form(...), session: Session = Depends(get_session)):
    """HTMX endpoint to buy a monkey upgrade."""
    player = session.get(Player, player_id)
    upgrade = session.get(MonkeyUpgrade, upgrade_id)
    if not player or not upgrade:
        return HTMLResponse(content="Error", status_code=400)
    
    # Calcula custo atual baseado na quantidade
    owned = session.exec(select(PlayerUpgrade).where(PlayerUpgrade.player_id == player_id, PlayerUpgrade.upgrade_id == upgrade_id)).first()
    qty = owned.quantity if owned else 0
    current_cost = int(upgrade.base_cost * (1.15 ** qty))
    
    # Sempre sincroniza a contagem atual de bananas antes de tentar comprar
    if bananas_count > player.bananas_count:
        player.bananas_count = bananas_count
    
    if player.bananas_count >= current_cost:
        player.bananas_count -= current_cost
        if owned:
            owned.quantity += 1
            session.add(owned)
        else:
            new_owned = PlayerUpgrade(player_id=player_id, upgrade_id=upgrade_id, quantity=1)
            session.add(new_owned)
        
    session.add(player)
    session.commit()
    session.refresh(player)
    
    upgrades = session.exec(select(MonkeyUpgrade)).all()
    owned_rows = session.exec(select(PlayerUpgrade).where(PlayerUpgrade.player_id == player.id)).all()
    owned_upgrades = {row.upgrade_id: row.quantity for row in owned_rows}
    
    boosts = {}
    click_power = 1
    
    # Calcula modificadores
    for upg in upgrades:
        qty = owned_upgrades.get(upg.id, 0)
        if upg.upgrade_type == "boost" and upg.boost_target:
            boosts[upg.boost_target] = boosts.get(upg.boost_target, 0) + (upg.boost_value * qty)
        elif upg.upgrade_type == "click":
            click_power += (upg.boost_value * qty)
            
    # Calcula bananas por segundo
    bps = 0
    for upg in upgrades:
        if upg.upgrade_type == "monkey":
            qty = owned_upgrades.get(upg.id, 0)
            eff_bps = upg.bananas_per_second + boosts.get(upg.name, 0)
            bps += eff_bps * qty

    # Retorna template do jogo
    return templates.TemplateResponse(request=request, name="game.html", context={
        "player": player,
        "upgrades": upgrades,
        "owned_upgrades": owned_upgrades,
        "bps": bps,
        "click_power": click_power,
        "message": "Compra realizada com sucesso!" if player.bananas_count >= current_cost else "Bananas insuficientes!"
    })

@app.get("/leaderboard", response_class=HTMLResponse)
def leaderboard(request: Request, page: int = 1, session: Session = Depends(get_session)):
    """HTMX endpoint to return the leaderboard page with pagination."""
    per_page = 5
    offset = (page - 1) * per_page
    
    # usando desc() do SQLModel
    players = session.exec(select(Player).order_by(Player.bananas_count.desc()).offset(offset).limit(per_page)).all() # type: ignore
    total_players = len(session.exec(select(Player)).all())
    
    has_next = (offset + per_page) < total_players
    has_prev = page > 1
    
    return templates.TemplateResponse(request=request, name="partials/leaderboard.html", context={
        "players": players,
        "page": page,
        "has_next": has_next,
        "has_prev": has_prev
    })

@app.delete("/player/{player_id}", response_class=HTMLResponse)
def delete_player(request: Request, player_id: int, session: Session = Depends(get_session)):
    """HTMX endpoint to delete profile."""
    player = session.get(Player, player_id)
    if player:
        # Deleta upgrades
        owned = session.exec(select(PlayerUpgrade).where(PlayerUpgrade.player_id == player_id)).all()
        for o in owned:
            session.delete(o)
        session.delete(player)
        session.commit()
    # Retorna snippet para recarregar a página ou mostrar mensagem de sucesso
    return HTMLResponse(content='<script>window.location.href="/";</script>', status_code=200)

