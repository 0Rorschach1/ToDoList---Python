from __future__ import annotations

import os
from datetime import datetime
from typing import List, Optional

from task import Task
from exception import MaxLimitExceededError, ValidationError, TaskNotFoundError

class Project:
    def __init__(self, *, name: str, description: str, container_user: Optional[User] = None):
        self.validate_name(name)
        self.validate_description(description)
        self.name = name.strip()
        self.description = description.strip()
        self.created_at = datetime.now()
        self.tasks: List[Task] = []
        self.container_user: Optional[User] = None
        self.id = id(self)  # Unique project ID
        if container_user:
            self.set_user(container_user)

    @staticmethod
    def validate_name(name: str):
        if len(name.strip()) < 30:
            raise ValidationError("Project name must be at least 30 characters.")

    @staticmethod
    def validate_description(description: str):
        if len(description.strip()) < 150:
            raise ValidationError("Project description must be at least 150 characters.")

    def set_user(self, user: User):
        from user import User
        if not isinstance(user, User):
            raise ValueError("container_user must be a User instance.")
        if self.container_user:
            while self in self.container_user.projects:
                self.container_user.projects.remove(self)
        self.container_user = user
        if self not in user.projects:
            user.projects.append(self)

    def add_task(self, task: Task):
        if not isinstance(task, Task):
            raise ValueError("Only Task instances can be added.")
        if task in self.tasks:
            raise ValueError("Task already exists in this project.")
        if task.container_project:
            while task in task.container_project.tasks:
                task.container_project.tasks.remove(task)
        max_tasks = int(os.getenv("TASK_OF_NUMBER_MAX", 20))
        if len(self.tasks) >= max_tasks:
            raise MaxLimitExceededError(f"Cannot add more than {max_tasks} tasks to a project.")
        task.container_project = self
        self.tasks.append(task)

    def delete_project(self):
        for task in self.tasks[:]:
            task.delete_task()
        self.tasks.clear()
        if self.container_user:
            while self in self.container_user.projects:
                self.container_user.projects.remove(self)

    def delete_task_by_id(self, task_id: int):
        for task in self.tasks:
            if task.id == task_id:
                return task.delete_task()
        raise TaskNotFoundError(f"Task with ID {task_id} not found in project {self.name}.")

    def edit(self, *, new_name: Optional[str] = None, new_description: Optional[str] = None, new_user: Optional[User] = None):
        if new_name:
            self.validate_name(new_name)
            new_name = new_name.strip()
            if self.container_user:
                for p in self.container_user.projects:
                    if p != self and p.name == new_name:
                        raise ValueError("Project name must be unique for this user.")
            self.name = new_name

        if new_description:
            self.validate_description(new_description)
            self.description = new_description.strip()

        if new_user:
            self.set_user(new_user)

    def show_tasks(self) -> List[Task]:
        if not self.tasks:
            print(f"No tasks found in project '{self.name}'.")
            return []
        return self.tasks

    def __str__(self):
        return f"Project ID: {self.id} | Name: {self.name} | Description: {self.description[:50]}... | Tasks: {len(self.tasks)}"
