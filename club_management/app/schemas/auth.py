from pydantic import BaseModel, EmailStr, Field, ConfigDict

class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    refresh_token: str = Field(min_length=1, max_length=4096)
