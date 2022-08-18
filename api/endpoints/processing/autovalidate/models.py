from pydantic import BaseModel


class InsertModel(BaseModel):
    min: float
    max: float
    rep: int
    pollutant_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)


class DeleteModel(BaseModel):
    id: int

    def __getitem__(self, key):
        return super().__getattribute__(key)


class UpdateModel(BaseModel):
    id: int
    min: float
    max: float
    rep: int

    def __getitem__(self, key):
        return super().__getattribute__(key)
