from pydantic import BaseModel


class AssessmentRegimeModel(BaseModel):
    id: str
    name: str
    objecttype: str
    reportingmetric: str
    protectiontarget: str
    assessmentthresholdexceedance: str
    include: bool
    thresholdclassificationyear: str
    thresholdclassificationreport: str
    zoneid: str
    zone_name: str
    pollutant: str
    pollutant_name: str
    data: list

    def __getitem__(self, key):
        return super().__getattribute__(key)


class DeleteModel(BaseModel):
    id: str

    def __getitem__(self, key):
        return super().__getattribute__(key)
