import os
import uuid
from datetime import datetime
from typing import List, Optional, Tuple
from dotenv import load_dotenv

from user import User
from task import Task
from exceptions import MaxLimitExceededError

# Load environment variables
load_dotenv()


class Project:
    def __init__(self, *, name: str, description: str, container_user: Optional[User] = None):
        self.name = name.strip()
        self.description = description.strip()
        self.created_at = datetime.now()
        self.tasks: List[Task] = []
        self.container_user: Optional[User] = None
        if container_user:
            self.set_user(container_user)

    def set_user(self, user: User):
        if not isinstance(user, User):
            raise ValueError("container_user must be a User instance.")
        if self.container_user and self in self.container_user.projects:
            self.container_user.projects.remove(self)
        self.container_user = user
        user.projects.append(self)

    def add_task(self, task: Task):
        if not isinstance(task, Task):
            raise ValueError("Only Task instances can be added.")
        if task in self.tasks:
            raise ValueError("Task already exists in this project.")
        max_tasks = int(os.getenv("MAX_NUMBER_OF_TASKS", 20))
        if len(self.tasks) >= max_tasks:
            raise MaxLimitExceededError(f"Cannot add more than {max_tasks} tasks to a project.")
        task.container_project = self
        self.tasks.append(task)

    def delete_project(self):
        # Cascade delete tasks
        for task in self.tasks:
            task.delete_task()
        self.tasks.clear()
        # Remove project from user's list
        if self.container_user and self in self.container_user.projects:
            self.container_user.projects.remove(self)
        del self


class ProjectManager:
    def __init__(self):
        self.projects: List[Project] = []
        try:
            self.max_projects = int(os.getenv("MAX_NUMBER_OF_PROJECTS", 10))
        except ValueError:
            self.max_projects = 10

    def is_project_name_unique(self, name: str, user: Optional[User] = None, exclude_name: Optional[str] = None) -> bool:
        """Check uniqueness for a user (if provided)"""
        projects = user.projects if user else self.projects
        return all(p.name != name or (exclude_name and p.name == exclude_name) for p in projects)

    def edit_project(self, project_name: str, new_name: str, new_description: str) -> dict:
        for project in self.projects:
            if project.name == project_name:
                if not self.is_project_name_unique(new_name, project.container_user, exclude_name=project_name):
                    return {"status": "error", "message": "Project name must be unique."}
                project.name = new_name.strip()
                project.description = new_description.strip()
                return {"status": "success", "message": f"Project '{new_name}' updated successfully."}
        return {"status": "error", "message": "Project not found."}

    def get_project_tasks(self, project_name: str) -> Tuple[Optional[List[Task]], Optional[str]]:
        for project in self.projects:
            if project.name == project_name:
                return project.tasks, project.name
        return None, None
