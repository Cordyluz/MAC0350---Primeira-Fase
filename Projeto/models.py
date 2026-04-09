from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class PlayerUpgrade(SQLModel, table=True):
    player_id: Optional[int] = Field(
        default=None, foreign_key="player.id", primary_key=True
    )
    upgrade_id: Optional[int] = Field(
        default=None, foreign_key="monkeyupgrade.id", primary_key=True
    )
    quantity: int = Field(default=0)

class MonkeyUpgrade(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    base_cost: int
    bananas_per_second: int
    image_url: str
    
    upgrade_type: str = Field(default="monkey") # "monkey", "click", "boost"
    boost_target: Optional[str] = Field(default=None)
    boost_value: int = Field(default=0)

class Player(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    bananas_count: int = Field(default=0)
    
