from models import Project, Task, db

def recalculate_project_progress_and_status(project):
    """
    Recalculates completion_progress and status for a project based on its tasks and project dependencies.
    """
    tasks = Task.query.filter_by(project_id=project.id).all()

    if not tasks:
        project.completion_progress = 0.0
        project.status = 'Draft'
        return

    # Calculate Progress: (sum of weights of Done tasks / total sum of weights) * 100
    total_weight = sum(t.weight for t in tasks)
    done_weight = sum(t.weight for t in tasks if t.status == 'Done')

    if total_weight > 0:
        project.completion_progress = (done_weight / total_weight) * 100.0
    else:
        project.completion_progress = 0.0

    # Determine candidate status from tasks:
    # - Draft: all tasks are Draft
    # - Done: all tasks are Done
    # - In Progress: at least one task is In Progress, OR mix of Done & Draft/In Progress
    statuses = set(t.status for t in tasks)

    if statuses == {'Draft'}:
        candidate_status = 'Draft'
    elif statuses == {'Done'}:
        candidate_status = 'Done'
    else:
        candidate_status = 'In Progress'

    # Apply Project Dependency Rule:
    # "Project tidak dapat berstatus In Progress atau Done jika dependency project belum Done."
    if candidate_status in ('In Progress', 'Done'):
        not_done_project_deps = [dep for dep in project.depends_on if dep.status != 'Done']
        if not_done_project_deps:
            # Downgrade to Draft because prerequisite project is not Done yet
            candidate_status = 'Draft'

    old_status = project.status
    project.status = candidate_status

    # If project status changed, propagate recalculation to dependent projects
    if old_status != candidate_status:
        db.session.flush() # ensure current state is flushed
        for dep_project in project.dependent_projects.all():
            recalculate_project_progress_and_status(dep_project)


def recalculate_all_dependent_projects(project_id):
    """
    Triggers cascading recalculation for all projects depending on project_id.
    """
    project = Project.query.get(project_id)
    if not project:
        return
    
    for dep_project in project.dependent_projects.all():
        recalculate_project_progress_and_status(dep_project)
