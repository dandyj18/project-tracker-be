from models import db, Task

class TaskRepository:
    @staticmethod
    def get_all(project_id=None):
        query = Task.query
        if project_id:
            query = query.filter(Task.project_id == project_id)
        return query.all()

    @staticmethod
    def get_top_level_tasks(project_id=None):
        query = Task.query
        if project_id:
            query = query.filter(Task.project_id == project_id)
        return query.filter(Task.parent_id.is_(None)).all()

    @staticmethod
    def get_by_id(task_id):
        return Task.query.get(task_id)

    @staticmethod
    def get_by_ids(task_ids):
        if not task_ids:
            return []
        return Task.query.filter(Task.id.in_(task_ids)).all()

    @staticmethod
    def create(project_id, name, status='Draft', weight=1, parent_id=None, depends_on_tasks=None):
        task = Task(
            project_id=project_id,
            parent_id=parent_id if parent_id else None,
            name=name,
            status=status,
            weight=weight
        )
        if depends_on_tasks:
            task.depends_on = depends_on_tasks

        db.session.add(task)
        return task

    @staticmethod
    def update(task, name=None, status=None, weight=None, parent_id=None, depends_on_tasks=None):
        if name is not None:
            task.name = name
        if status is not None:
            task.status = status
        if weight is not None:
            task.weight = weight
        if parent_id is not None:
            task.parent_id = parent_id if parent_id else None
        if depends_on_tasks is not None:
            task.depends_on = depends_on_tasks
        return task

    @staticmethod
    def delete(task):
        db.session.delete(task)

    @staticmethod
    def commit():
        db.session.commit()
