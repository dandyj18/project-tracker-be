from app import create_app
from models import db
from services.calculator import recalculate_project_progress_and_status
from .project_seeder import ProjectSeeder
from .task_seeder import TaskSeeder

class DatabaseSeeder:
    @staticmethod
    def run():
        app = create_app()
        with app.app_context():
            print("Resetting database tables...")
            db.drop_all()
            db.create_all()

            # Seed Projects
            p1, p2 = ProjectSeeder.run()

            # Seed Tasks
            TaskSeeder.run(p1, p2)

            # Recalculate status & progress for projects
            recalculate_project_progress_and_status(p1)
            recalculate_project_progress_and_status(p2)
            db.session.commit()

            print("Database seeded successfully!")
            print(f"Project 1 Progress: {p1.completion_progress:.1f}%, Status: {p1.status}")
            print(f"Project 2 Status (Dependent on P1): {p2.status}")
