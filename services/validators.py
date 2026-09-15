from models import Project, Task, db
from datetime import datetime

def parse_date(date_str):
    if isinstance(date_str, datetime):
        return date_str.date()
    if hasattr(date_str, 'year'):
        return date_str
    return datetime.strptime(str(date_str), '%Y-%m-%d').date()

def validate_project_schedule(start_date_input, end_date_input, project_id=None):
    """
    Validates that:
    1. start_date <= end_date
    2. No existing project date range intersects with [start_date, end_date]
    Returns (is_valid: bool, error_message: str)
    """
    try:
        start_date = parse_date(start_date_input)
        end_date = parse_date(end_date_input)
    except Exception:
        return False, "Format tanggal tidak valid. Gunakan format YYYY-MM-DD."

    if start_date > end_date:
        return False, "Tanggal mulai (start_date) tidak boleh lebih besar dari tanggal selesai (end_date)."

    # Query all existing projects except current project_id
    query = Project.query
    if project_id:
        query = query.filter(Project.id != project_id)
    
    existing_projects = query.all()

    for p in existing_projects:
        # Intersect condition: (start1 <= end2) and (end1 >= start2)
        if (start_date <= p.end_date) and (end_date >= p.start_date):
            return False, f"Konflik jadwal! Berbenturan dengan Project '{p.name}' ({p.start_date.strftime('%Y-%m-%d')} s/d {p.end_date.strftime('%Y-%m-%d')})."

    return True, None


def detect_project_circular_dependency(source_project_id, target_depends_on_ids):
    """
    Checks if adding dependencies target_depends_on_ids to source_project_id introduces a cycle.
    A cycle exists if source_project_id is reachable from any target_depends_on_id.
    """
    if source_project_id in target_depends_on_ids:
        return True, "Project tidak dapat bergantung pada dirinya sendiri."

    for target_id in target_depends_on_ids:
        visited = set()
        stack = [target_id]

        while stack:
            curr_id = stack.pop()
            if curr_id == source_project_id:
                target_proj = Project.query.get(target_id)
                target_name = target_proj.name if target_proj else f"ID {target_id}"
                return True, f"Terdeteksi circular dependency antar project (Project ID {source_project_id} <-> {target_name})."

            if curr_id not in visited:
                visited.add(curr_id)
                curr_proj = Project.query.get(curr_id)
                if curr_proj:
                    for dep in curr_proj.depends_on:
                        if dep.id not in visited:
                            stack.append(dep.id)

    return False, None


def detect_task_circular_dependency(source_task_id, target_depends_on_ids):
    """
    Checks if adding dependencies target_depends_on_ids to source_task_id introduces a cycle.
    """
    if source_task_id in target_depends_on_ids:
        return True, "Task tidak dapat bergantung pada dirinya sendiri."

    for target_id in target_depends_on_ids:
        visited = set()
        stack = [target_id]

        while stack:
            curr_id = stack.pop()
            if curr_id == source_task_id:
                target_task = Task.query.get(target_id)
                target_name = target_task.name if target_task else f"ID {target_id}"
                return True, f"Terdeteksi circular dependency antar task (Task ID {source_task_id} <-> '{target_name}')."

            if curr_id not in visited:
                visited.add(curr_id)
                curr_task = Task.query.get(curr_id)
                if curr_task:
                    for dep in curr_task.depends_on:
                        if dep.id not in visited:
                            stack.append(dep.id)

    return False, None


def validate_task_status_transition(task, new_status):
    """
    Ensures a task cannot be changed to 'Done' if any of its dependency tasks are not 'Done'.
    """
    if new_status == 'Done':
        not_done_deps = [dep for dep in task.depends_on if dep.status != 'Done']
        if not_done_deps:
            dep_names = ", ".join([f"'{d.name}' ({d.status})" for d in not_done_deps])
            return False, f"Task '{task.name}' tidak dapat diubah ke status Done karena dependency task berikut belum Done: {dep_names}."
    return True, None
