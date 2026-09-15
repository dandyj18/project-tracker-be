from repositories.task_repository import TaskRepository
from repositories.project_repository import ProjectRepository
from services.validators import detect_task_circular_dependency, validate_task_status_transition
from services.calculator import recalculate_project_progress_and_status

class TaskController:
    @staticmethod
    def prune_task_tree(task, status_filter, search_query):
        """
        Recursively filters a task and its subtasks.
        Rule 3: "Hasil filtering harus konsisten secara hierarkis: jika subtask match, parent tetap ditampilkan (meskipun parent tidak match)."
        """
        status_filter = status_filter or 'All'
        search_query = (search_query or '').strip().lower()

        # Self matching logic
        status_match = (status_filter == 'All') or (task.status == status_filter)
        search_match = (not search_query) or (search_query in task.name.lower())
        self_matches = status_match and search_match

        # Process child subtasks recursively
        matching_subtasks = []
        for child in task.subtasks:
            pruned_child = TaskController.prune_task_tree(child, status_filter, search_query)
            if pruned_child is not None:
                matching_subtasks.append(pruned_child)

        # Node is retained if it matches itself OR has any matching subtask
        if self_matches or len(matching_subtasks) > 0:
            task_dict = task.to_dict(include_subtasks=False)
            task_dict['subtasks'] = matching_subtasks
            return task_dict

        return None

    @staticmethod
    def get_all_tasks(project_id=None, status_filter=None, search_query=None):
        top_level_tasks = TaskRepository.get_top_level_tasks(project_id)

        filtered_tasks = []
        for task in top_level_tasks:
            pruned = TaskController.prune_task_tree(task, status_filter, search_query)
            if pruned is not None:
                filtered_tasks.append(pruned)

        return {
            'success': True,
            'data': filtered_tasks
        }, 200

    @staticmethod
    def get_task_by_id(task_id):
        task = TaskRepository.get_by_id(task_id)
        if not task:
            return {'success': False, 'message': 'Task tidak ditemukan.'}, 404
        return {
            'success': True,
            'data': task.to_dict(include_subtasks=True)
        }, 200

    @staticmethod
    def create_task(data):
        data = data or {}
        project_id = data.get('project_id')
        name = data.get('name', '').strip()
        status = data.get('status', 'Draft')
        weight = data.get('weight', 1)
        parent_id = data.get('parent_id')
        depends_on_ids = data.get('depends_on', [])

        if not project_id:
            return {'success': False, 'message': 'Project ID wajib diisi.'}, 400
        if not name:
            return {'success': False, 'message': 'Nama task wajib diisi.'}, 400

        project = ProjectRepository.get_by_id(project_id)
        if not project:
            return {'success': False, 'message': 'Project tidak ditemukan.'}, 404

        try:
            weight = int(weight)
            if weight < 0:
                return {'success': False, 'message': 'Bobot task harus bernilai minimal 0.'}, 400
        except ValueError:
            return {'success': False, 'message': 'Bobot task harus berupa angka.'}, 400

        if status not in ('Draft', 'In Progress', 'Done'):
            return {'success': False, 'message': 'Status task tidak valid.'}, 400

        dep_tasks = TaskRepository.get_by_ids(depends_on_ids) if depends_on_ids else []

        task = TaskRepository.create(
            project_id=project_id,
            name=name,
            status=status,
            weight=weight,
            parent_id=parent_id,
            depends_on_tasks=dep_tasks
        )

        # Validate task dependency status rules
        is_valid_transition, transition_err = validate_task_status_transition(task, status)
        if not is_valid_transition:
            return {'success': False, 'message': transition_err}, 400

        TaskRepository.commit()

        # Recalculate project progress & status
        recalculate_project_progress_and_status(project)
        TaskRepository.commit()

        return {
            'success': True,
            'message': 'Task berhasil dibuat.',
            'data': task.to_dict()
        }, 201

    @staticmethod
    def update_task(task_id, data):
        task = TaskRepository.get_by_id(task_id)
        if not task:
            return {'success': False, 'message': 'Task tidak ditemukan.'}, 404

        data = data or {}
        name = data.get('name', task.name).strip()
        status = data.get('status', task.status)
        weight = data.get('weight', task.weight)
        parent_id = data.get('parent_id', task.parent_id)
        depends_on_ids = data.get('depends_on', [t.id for t in task.depends_on])

        if not name:
            return {'success': False, 'message': 'Nama task wajib diisi.'}, 400

        try:
            weight = int(weight)
            if weight < 0:
                return {'success': False, 'message': 'Bobot task tidak boleh kurang dari 0.'}, 400
        except ValueError:
            return {'success': False, 'message': 'Bobot task harus berupa angka.'}, 400

        if parent_id == task_id:
            return {'success': False, 'message': 'Task tidak dapat menjadi parent dari dirinya sendiri.'}, 400

        # Validate task circular dependency rule
        is_cycle, cycle_err = detect_task_circular_dependency(task_id, depends_on_ids)
        if is_cycle:
            return {'success': False, 'message': cycle_err}, 400

        dep_tasks = TaskRepository.get_by_ids(depends_on_ids) if depends_on_ids else []
        task.depends_on = dep_tasks

        # Validate status transition rule (Task Dependency Rule 1)
        is_valid_transition, transition_err = validate_task_status_transition(task, status)
        if not is_valid_transition:
            return {'success': False, 'message': transition_err}, 400

        TaskRepository.update(
            task,
            name=name,
            status=status,
            weight=weight,
            parent_id=parent_id,
            depends_on_tasks=dep_tasks
        )

        TaskRepository.commit()

        # Recalculate dependent tasks status if this task status changed
        if status != 'Done':
            for dependent_t in task.dependent_tasks.all():
                if dependent_t.status == 'Done':
                    dependent_t.status = 'In Progress'

        # Recalculate project progress & status
        recalculate_project_progress_and_status(task.project)
        TaskRepository.commit()

        return {
            'success': True,
            'message': 'Task berhasil diperbarui.',
            'data': task.to_dict()
        }, 200

    @staticmethod
    def delete_task(task_id):
        task = TaskRepository.get_by_id(task_id)
        if not task:
            return {'success': False, 'message': 'Task tidak ditemukan.'}, 404

        task_name = task.name
        project = task.project

        TaskRepository.delete(task)
        TaskRepository.commit()

        # Recalculate project progress & status after deletion
        recalculate_project_progress_and_status(project)
        TaskRepository.commit()

        return {
            'success': True,
            'message': f"Task '{task_name}' berhasil dihapus."
        }, 200
