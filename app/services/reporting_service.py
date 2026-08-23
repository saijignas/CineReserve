"""Reporting service for admin analytics."""
from sqlalchemy.orm import Session
from typing import Dict, Any, Optional
from datetime import date
from app.repositories.reporting_repository import ReportingRepository


class ReportingService:
    """Reporting service."""

    def __init__(self, db: Session):
        self.db = db
        self.reporting_repo = ReportingRepository()

    def get_revenue_report(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        movie_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get revenue report."""
        return self.reporting_repo.get_revenue_report(
            db=self.db,
            start_date=start_date,
            end_date=end_date,
            movie_id=movie_id
        )

    def get_capacity_report(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        movie_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get capacity utilization report."""
        return self.reporting_repo.get_capacity_report(
            db=self.db,
            start_date=start_date,
            end_date=end_date,
            movie_id=movie_id
        )
