from models import db, Project

class ProjectRepository:
    @staticmethod
    def get_all(status_filter=None, search_query=None):
        query = Project.query.order_by(Project.start_date.asc())

        if status_filter and status_filter != 'All':
            query = query.filter(Project.status == status_filter)
        
        if search_query:
            query = query.filter(Project.name.ilike(f'%{search_query}%'))

        return query.all()

    @staticmethod
    def get_by_id(project_id):
        return Project.query.get(project_id)

    @staticmethod
    def get_by_ids(project_ids):
        if not project_ids:
            return []
        return Project.query.filter(Project.id.in_(project_ids)).all()

    @staticmethod
    def create(name, start_date, end_date, depends_on_projects=None):
        project = Project(
            name=name,
            start_date=start_date,
            end_date=end_date,
            status='Draft',
            completion_progress=0.0
        )
        if depends_on_projects:
            project.depends_on = depends_on_projects
            
        db.session.add(project)
        return project

    @staticmethod
    def update(project, name=None, start_date=None, end_date=None, depends_on_projects=None):
        if name is not None:
            project.name = name
        if start_date is not None:
            project.start_date = start_date
        if end_date is not None:
            project.end_date = end_date
        if depends_on_projects is not None:
            project.depends_on = depends_on_projects
        return project

    @staticmethod
    def delete(project):
        db.session.delete(project)

    @staticmethod
    def commit():
        db.session.commit()

    @staticmethod
    def flush():
        db.session.flush()
