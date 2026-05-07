from typing import Optional, List
from core.base_model import RavenBaseModel


class CreateGroupModel(RavenBaseModel):
    name: str
    sampling_point_ids: Optional[List[str]] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)


class UpdateGroupModel(RavenBaseModel):
    id: str
    name: str

    def __getitem__(self, key):
        return super().__getattribute__(key)


class DeleteGroupModel(RavenBaseModel):
    id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)


class AddMemberModel(RavenBaseModel):
    sampling_point_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)


class RemoveMemberModel(RavenBaseModel):
    sampling_point_id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
