from .base import CRUDBase
from app.models.report import Report
from app.schemas.report import ReportCreate, ReportUpdate

class CRUDReport(CRUDBase[Report, ReportCreate, ReportUpdate]):
    pass

report = CRUDReport(Report)
