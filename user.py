import os
from typing import List, Optional
from dotenv import load_dotenv

from project import Project
from task import Task
from exceptions import MaxLimitExceededError

# Load environment variables
load_dotenv()


class User:
    def __init__(self, username: str):
        """
        Initialize a User instance.
        :param username: Unique username for the user.
        """
        self.username: str = username
        self.projects: List[Project] = []

    def create_project(self, name: str, description: str) -> Project:
        """
        Create a new project for this user.
        :param name: Project name (must be unique for this user, ≥30 chars)
        :param description: Project description (≥150 chars)
        :return: Project instance
        :raises ValueError: If name/description validation fails or name is not unique
        :raises MaxLimitExceededError: If user exceeds max projects limit
        """
        # Validate length
        if len(name.strip()) < 30 or len(description.strip()) < 150:
            raise ValueError("Project name must be ≥30 chars and description ≥150 chars.")

        # Check unique project name
        for project in self.projects:
            if project.name == name.strip():
                raise ValueError("Project name must be unique for this user.")

        # Check max projects
        max_projects = int(os.getenv("MAX_NUMBER_OF_PROJECTS", 10))
        if len(self.projects) >= max_projects:
            raise MaxLimitExceededError(f"Cannot have more than {max_projects} projects for this user.")

        # Create project and link to this user
        project = Project(name=name.strip(), description=description.strip(), container_user=self)
        self.projects.append(project)
        return project

    def get_project_by_name(self, name: str) -> Optional[Project]:
        """
        Retrieve a project by its name.
        :param name: Name of the project
        :return: Project instance or None if not found
        """
        for project in self.projects:
            if project.name == name:
                return project
        return None

    def edit_project(self, project_name: str, new_name: str, new_description: str) -> dict:
        """
        Edit an existing project identified by its name.
        :param project_name: Current project name
        :param new_name: New project name
        :param new_description: New description
        :return: dict with status and message
        """
        project = self.get_project_by_name(project_name)
        if not project:
            return {"status": "error", "message": "Project not found."}

        # Check uniqueness
        for p in self.projects:
            if p.name == new_name.strip() and p != project:
                return {"status": "error", "message": "Project name must be unique."}

        project.name = new_name.strip()
        project.description = new_description.strip()
        return {"status": "success", "message": f"Project '{new_name}' updated successfully."}

    def list_projects(self) -> None:
        """
        Display all projects of the user with task count.
        """
        if not self.projects:
            print(f"User '{self.username}' has no projects.")
            return

        print(f"Projects for user '{self.username}':")
        for project in sorted(self.projects, key=lambda p: p.created_at):
            print(f"- {project.name} | Tasks: {len(project.tasks)} | Created: {project.created_at}")

    def __str__(self):
        return f"User: {self.username} | Projects: {len(self.projects)}"

    def __repr__(self):
        return self.__str__()
