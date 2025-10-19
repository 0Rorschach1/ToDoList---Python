import os
from datetime import datetime
from typing import List, Optional
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

    def edit(self, *,
             new_name: Optional[str] = None,
             new_description: Optional[str] = None,
             new_user: Optional[User] = None):
        """
        Edit project attributes.
        :param new_name: New name of the project (must be unique for the user)
        :param new_description: New description
        :param new_user: Change container_user
        """
        # Change name
        if new_name:
            new_name = new_name.strip()
            if self.container_user:
                # Ensure uniqueness among user's projects
                for p in self.container_user.projects:
                    if p != self and p.name == new_name:
                        raise ValueError("Project name must be unique for this user.")
            self.name = new_name

        # Change description
        if new_description:
            self.description = new_description.strip()

        # Change user
        if new_user:
            self.set_user(new_user)

    def show_tasks(self) -> List[Task]:
        """
        Return a list of tasks for this project.
        :return: List of Task instances
        """
        return self.tasks
