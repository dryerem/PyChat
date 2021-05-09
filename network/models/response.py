from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel


class AuthResponse(BaseModel):
    access: bool