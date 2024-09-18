from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    ForeignKey
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
    __tablename__ = 'desktops'

    id = Column(Integer, primary_key=True)
    user_id = Column(String, default=None)
    name = Column(String, default=None)
    occupied = Column(Boolean, default=False)


class TempDesktopSelection(Base):
    """
    A model representing a temporary desktop selection by a user.
    
    Attributes:
        id (int): The unique identifier for the temporary selection.
        user_id (str): The ID of the user making the selection.
        desktop_id (int): The ID of the desktop being selected.
    """
    __tablename__ = 'temp_desktop_selections'

    id = Column(Integer, primary_key=True)
    user_id = Column(String, unique=True, nullable=False)
    desktop_id = Column(Integer, ForeignKey('desktops.id'), nullable=False)