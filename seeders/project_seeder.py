from datetime import date
from models import db, Project
from repositories.project_repository import ProjectRepository

class ProjectSeeder:
    @staticmethod
    def run():
        print("Seeding projects...")
        p1 = ProjectRepository.create(
            name="Platform E-Commerce Modern",
            start_date=date(2026, 10, 1),
            end_date=date(2026, 10, 15)
        )

        p2 = ProjectRepository.create(
            name="Aplikasi Mobile Android & iOS",
            start_date=date(2026, 10, 16),
            end_date=date(2026, 10, 31)
        )

        ProjectRepository.commit()

        # Set project dependencies: p2 depends on p1
        p2.depends_on.append(p1)
        ProjectRepository.commit()

        return p1, p2
