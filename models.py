# Re-export models from the models package for backward compatibility
from models.db import db
from models.project import Project, ProjectDependency
from models.task import Task, TaskDependency

__all__ = ['db', 'Project', 'ProjectDependency', 'Task', 'TaskDependency']
