from core.base_model import RavenBaseModel


class FavoriteInsertModel(RavenBaseModel):

    name: str
    config: dict

    def __getitem__(self, key):
        return super().__getattribute__(key)


class FavoriteUpdateModel(RavenBaseModel):

    id: int
    name: str
    config: dict

    def __getitem__(self, key):
        return super().__getattribute__(key)


class FavoriteDeleteModel(RavenBaseModel):

    id: int

    def __getitem__(self, key):
        return super().__getattribute__(key)
