from repositories.task_repository import TaskRepository

class TaskSeeder:
    @staticmethod
    def run(p1, p2):
        print("Seeding tasks...")
        # 1. Tasks for Project 1
        t1 = TaskRepository.create(
            project_id=p1.id,
            name="Desain UI/UX & Wireframing",
            status="Done",
            weight=2
        )
        TaskRepository.commit()

        t2 = TaskRepository.create(
            project_id=p1.id,
            name="Development Frontend Web SPA",
            status="In Progress",
            weight=1
        )
        TaskRepository.commit()

        # Subtasks under Task 2
        t2_1 = TaskRepository.create(
            project_id=p1.id,
            parent_id=t2.id,
            name="Slicing Component & Glassmorphism Theme",
            status="Done",
            weight=1
        )
        t2_2 = TaskRepository.create(
            project_id=p1.id,
            parent_id=t2.id,
            name="Integrasi State Management & REST API",
            status="In Progress",
            weight=1
        )
        TaskRepository.commit()

        # Task 3 (Testing QA) depends on Task 1 and Task 2
        t3 = TaskRepository.create(
            project_id=p1.id,
            name="Testing & Quality Assurance",
            status="Draft",
            weight=1
        )
        t3.depends_on.extend([t1, t2])
        TaskRepository.commit()

        # 2. Tasks for Project 2
        p2_t1 = TaskRepository.create(
            project_id=p2.id,
            name="Setup Framework Mobile & Authentication",
            status="Draft",
            weight=2
        )
        p2_t2 = TaskRepository.create(
            project_id=p2.id,
            name="Sinkronisasi Backend API Gateway",
            status="Draft",
            weight=1
        )
        TaskRepository.commit()

        return [t1, t2, t2_1, t2_2, t3, p2_t1, p2_t2]
