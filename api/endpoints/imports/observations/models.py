from pydantic import BaseModel
from api.core.data.processing.processvalue import Processvalue


class Processvalues(BaseModel):
    items: list[Processvalue]
