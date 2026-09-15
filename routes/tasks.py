from flask import Blueprint, request, jsonify
from controllers.task_controller import TaskController

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/api/tasks', methods=['GET'])
def get_tasks():
    project_id = request.args.get('project_id', type=int)
    status_filter = request.args.get('status')
    search_query = request.args.get('search')
    res, status_code = TaskController.get_all_tasks(project_id, status_filter, search_query)
    return jsonify(res), status_code

@tasks_bp.route('/api/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    res, status_code = TaskController.get_task_by_id(task_id)
    return jsonify(res), status_code

@tasks_bp.route('/api/tasks', methods=['POST'])
def create_task():
    data = request.json or {}
    res, status_code = TaskController.create_task(data)
    return jsonify(res), status_code

@tasks_bp.route('/api/tasks/<int:task_id>', methods=['PUT'])
def update_task(task_id):
    data = request.json or {}
    res, status_code = TaskController.update_task(task_id, data)
    return jsonify(res), status_code

@tasks_bp.route('/api/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    res, status_code = TaskController.delete_task(task_id)
    return jsonify(res), status_code
