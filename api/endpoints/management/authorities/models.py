"""AQR3 AUT Authority models.

The AQR3 key is (CountryCode, AuthorityInstanceId, AuthorityRole, Email). CountryCode
is instance-wide (settings.country_code_id), so `id`, `authority_role_id` and `email`
together identify a row. All three are editable, hence the separate key/values shape
on update — an UPDATE keyed on the new values would match nothing and leave the
original row in place.
"""
from typing import Optional

from core.base_model import RavenBaseModel


class AuthorityKey(RavenBaseModel):
    """Identifies an existing authority."""
    id: str
    authority_role_id: str
    email: str

    def __getitem__(self, key):
        return super().__getattribute__(key)


class AuthorityModel(RavenBaseModel):

    # The three key columns, all NOT NULL in the schema.
    id: str
    authority_role_id: str
    email: str

    authority_name: str

    # Nullable in the schema, and Manager.vue turns a blank field into null before
    # posting, so these have to accept it — declaring them required `str` rejected a
    # row the database would have taken.
    person_name: Optional[str] = None
    authority_url: Optional[str] = None
    authority_address: Optional[str] = None
    authority_instance_id: Optional[str] = None
    authority_status_id: Optional[str] = None

    def __getitem__(self, key):
        return super().__getattribute__(key)
