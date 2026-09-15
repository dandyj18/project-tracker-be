from repositories.project_repository import ProjectRepository
from services.validators import validate_project_schedule, detect_project_circular_dependency, parse_date
from services.calculator import recalculate_project_progress_and_status, recalculate_all_dependent_projects

class ProjectController:
    @staticmethod
    def get_all_projects(status_filter=None, search_query=None):
        projects = ProjectRepository.get_all(status_filter, search_query)
        return {
            'success': True,
            'data': [p.to_dict(include_tasks=True) for p in projects]
        }, 200

    @staticmethod
    def get_project_by_id(project_id):
        project = ProjectRepository.get_by_id(project_id)
        if not project:
            return {'success': False, 'message': 'Project tidak ditemukan.'}, 404
        return {
            'success': True,
            'data': project.to_dict(include_tasks=True)
        }, 200

    @staticmethod
    def create_project(data):
        data = data or {}
        name = data.get('name', '').strip()
        start_date_str = data.get('start_date')
        end_date_str = data.get('end_date')
        depends_on_ids = data.get('depends_on', [])

        if not name:
            return {'success': False, 'message': 'Nama project wajib diisi.'}, 400
        if not start_date_str or not end_date_str:
            return {'success': False, 'message': 'Tanggal mulai dan selesai wajib diisi.'}, 400

        # Validate schedule non-intersection rule
        is_valid_schedule, schedule_err = validate_project_schedule(start_date_str, end_date_str)
        if not is_valid_schedule:
            return {'success': False, 'message': schedule_err}, 400

        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)

        # Get dependent project instances
        dep_projects = ProjectRepository.get_by_ids(depends_on_ids) if depends_on_ids else []

        # Create project
        project = ProjectRepository.create(
            name=name,
            start_date=start_date,
            end_date=end_date,
            depends_on_projects=dep_projects
        )
        ProjectRepository.commit()

        # Recalculate status & progress based on dependencies & empty tasks
        recalculate_project_progress_and_status(project)
        ProjectRepository.commit()

        return {
            'success': True,
            'message': 'Project berhasil dibuat.',
            'data': project.to_dict()
        }, 201

    @staticmethod
    def update_project(project_id, data):
        project = ProjectRepository.get_by_id(project_id)
        if not project:
            return {'success': False, 'message': 'Project tidak ditemukan.'}, 404

        data = data or {}
        name = data.get('name', project.name).strip()
        start_date_str = data.get('start_date', project.start_date.strftime('%Y-%m-%d'))
        end_date_str = data.get('end_date', project.end_date.strftime('%Y-%m-%d'))
        depends_on_ids = data.get('depends_on', [p.id for p in project.depends_on])

        if not name:
            return {'success': False, 'message': 'Nama project wajib diisi.'}, 400

        # 1. Validate schedule non-intersection rule
        is_valid_schedule, schedule_err = validate_project_schedule(start_date_str, end_date_str, project_id=project_id)
        if not is_valid_schedule:
            return {'success': False, 'message': schedule_err}, 400

        # 2. Validate project circular dependency rule
        is_cycle, cycle_err = detect_project_circular_dependency(project_id, depends_on_ids)
        if is_cycle:
            return {'success': False, 'message': cycle_err}, 400

        start_date = parse_date(start_date_str)
        end_date = parse_date(end_date_str)
        dep_projects = ProjectRepository.get_by_ids(depends_on_ids) if depends_on_ids else []

        ProjectRepository.update(
            project,
            name=name,
            start_date=start_date,
            end_date=end_date,
            depends_on_projects=dep_projects
        )

        # Recalculate status and progress
        recalculate_project_progress_and_status(project)
        ProjectRepository.commit()

        # Recalculate projects that depend on this updated project
        recalculate_all_dependent_projects(project_id)
        ProjectRepository.commit()

        return {
            'success': True,
            'message': 'Project berhasil diperbarui.',
            'data': project.to_dict()
        }, 200

    @staticmethod
    def delete_project(project_id):
        project = ProjectRepository.get_by_id(project_id)
        if not project:
            return {'success': False, 'message': 'Project tidak ditemukan.'}, 404

        project_name = project.name
        dependent_project_ids = [p.id for p in project.dependent_projects.all()]

        ProjectRepository.delete(project)
        ProjectRepository.commit()

        # Trigger recalculation on formerly dependent projects
        for dep_id in dependent_project_ids:
            dep_proj = ProjectRepository.get_by_id(dep_id)
            if dep_proj:
                recalculate_project_progress_and_status(dep_proj)
        ProjectRepository.commit()

        return {
            'success': True,
            'message': f"Project '{project_name}' berhasil dihapus."
        }, 200
