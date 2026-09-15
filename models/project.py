from datetime import datetime
from .db import db

class ProjectDependency(db.Model):
    __tablename__ = 'project_dependencies'
    
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), primary_key=True)
    depends_on_project_id = db.Column(db.Integer, db.ForeignKey('projects.id', ondelete='CASCADE'), primary_key=True)

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    status = db.Column(db.String(30), default='Draft', nullable=False) # 'Draft', 'In Progress', 'Done'
    completion_progress = db.Column(db.Float, default=0.0, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    tasks = db.relationship('Task', backref='project', cascade='all, delete-orphan', lazy=True)
    
    # Dependencies: Projects that THIS project depends on
    depends_on = db.relationship(
        'Project',
        secondary='project_dependencies',
        primaryjoin=(ProjectDependency.project_id == id),
        secondaryjoin=(ProjectDependency.depends_on_project_id == id),
        backref=db.backref('dependent_projects', lazy='dynamic'),
        lazy='joined'
    )

    def to_dict(self, include_tasks=True):
        data = {
            'id': self.id,
            'name': self.name,
            'status': self.status,
            'completion_progress': round(self.completion_progress, 1),
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'depends_on': [p.id for p in self.depends_on],
            'depends_on_details': [{'id': p.id, 'name': p.name, 'status': p.status} for p in self.depends_on]
        }
        if include_tasks:
            # Only top-level tasks (parent_id is None)
            top_level_tasks = [t for t in self.tasks if t.parent_id is None]
            data['tasks'] = [t.to_dict() for t in top_level_tasks]
        return data
