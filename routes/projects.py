from flask import Blueprint, request, jsonify
from controllers.project_controller import ProjectController

projects_bp = Blueprint('projects', __name__)

@projects_bp.route('/api/projects', methods=['GET'])
def get_projects():
    status_filter = request.args.get('status')
    search_query = request.args.get('search')
    res, status_code = ProjectController.get_all_projects(status_filter, search_query)
    return jsonify(res), status_code

@projects_bp.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    res, status_code = ProjectController.get_project_by_id(project_id)
    return jsonify(res), status_code

@projects_bp.route('/api/projects', methods=['POST'])
def create_project():
    data = request.json or {}
    res, status_code = ProjectController.create_project(data)
    return jsonify(res), status_code

@projects_bp.route('/api/projects/<int:project_id>', methods=['PUT'])
def update_project(project_id):
    data = request.json or {}
    res, status_code = ProjectController.update_project(project_id, data)
    return jsonify(res), status_code

@projects_bp.route('/api/projects/<int:project_id>', methods=['DELETE'])
def delete_project(project_id):
    res, status_code = ProjectController.delete_project(project_id)
    return jsonify(res), status_code
