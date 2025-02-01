""" Models """

from pydantic import BaseModel

class Proxy(BaseModel):
    """ Proxy object """
    host: str
    port: str
    username: str | None
    password: str | None

class TokenTask(BaseModel):
    """ AWS token task """
    goku_props: str
    site_host: str
    token_url: str
    captcha_url: str
    proxy: Proxy | str

class CaptchaTask(BaseModel):
    """ AWS captcha task """
    images: list[str]
    target: str
