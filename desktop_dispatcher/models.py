from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean
)    

from .session import Base


class Desktop(Base):
    """
    A model representing a desktop.

    Attributes:
        id (int): The unique identifier for the desktop.
        user_id (str): The ID of the user currently using the desktop.
        name (str): The name of the desktop.
        occupied (bool): Indicates whether the desktop is currently occupied.
    """
    __tablename__ = 'desktop'

    id = Column(Integer, primary_key=True)
    user_id = Column(String, default=None)
    name = Column(String, default=None)
    occupied = Column(Boolean, default=False)
