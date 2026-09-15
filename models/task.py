from datetime import datetime
from .db import db

class TaskDependency(db.Model):
    __tablename__ = 'task_dependencies'
    
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True)
    depends_on_task_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), primary_key=True)

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=True)
    name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(30), default='Draft', nullable=False) # 'Draft', 'In Progress', 'Done'
    weight = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Subtask hierarchy
    subtasks = db.relationship(
        'Task',
        backref=db.backref('parent', remote_side=[id]),
        cascade='all, delete-orphan',
        lazy='joined'
    )

    # Task dependencies: Tasks that THIS task depends on
    depends_on = db.relationship(
        'Task',
        secondary='task_dependencies',
        primaryjoin=(TaskDependency.task_id == id),
        secondaryjoin=(TaskDependency.depends_on_task_id == id),
        backref=db.backref('dependent_tasks', lazy='dynamic'),
        lazy='joined'
    )

    def to_dict(self, include_subtasks=True):
        data = {
            'id': self.id,
            'project_id': self.project_id,
            'parent_id': self.parent_id,
            'name': self.name,
            'status': self.status,
            'weight': self.weight,
            'depends_on': [t.id for t in self.depends_on],
            'depends_on_details': [{'id': t.id, 'name': t.name, 'status': t.status} for t in self.depends_on]
        }
        if include_subtasks:
            data['subtasks'] = [s.to_dict() for s in self.subtasks]
        return data
