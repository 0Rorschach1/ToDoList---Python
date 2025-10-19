import os
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv

from exceptions import MaxLimitExceededError

# Load environment variables
load_dotenv()


class Task:
    VALID_STATUSES = {"todo", "doing", "done"}

    def __init__(self, *, title: str, description: str,
                 status: str = "todo", deadline: Optional[str] = None):
        """
        Initialize a Task instance.
        :param title: Task title (≥30 chars)
        :param description: Task description (≥150 chars)
        :param status: Task status, defaults to "todo"
        :param deadline: Optional deadline in 'YYYY-MM-DD' format
        """
        self.validate_title(title)
        self.validate_description(description)
        self.title = title.strip()
        self.description = description.strip()
        self.status = "todo"  # default status
        self.set_status(status)  # validate & set
        self.created_at = datetime.now()
        self.deadline = None
        if deadline:
            self.set_deadline(deadline)
        self.container_project = None  # set when added to a project

    # ----------------- VALIDATIONS -----------------
    @staticmethod
    def validate_title(title: str):
        if len(title.strip()) < 30:
            raise ValueError("Task title must be at least 30 characters.")

    @staticmethod
    def validate_description(description: str):
        if len(description.strip()) < 150:
            raise ValueError("Task description must be at least 150 characters.")

    @staticmethod
    def validate_status(status: str):
        if status not in Task.VALID_STATUSES:
            raise ValueError(f"Status must be one of {Task.VALID_STATUSES}.")

    @staticmethod
    def validate_deadline(deadline: str):
        try:
            datetime.strptime(deadline, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Deadline must be a valid date in YYYY-MM-DD format.")

    # ----------------- SETTERS -----------------
    def set_status(self, status: str):
        status = status.strip().lower()
        self.validate_status(status)
        self.status = status

    def set_deadline(self, deadline: str):
        self.validate_deadline(deadline)
        self.deadline = datetime.strptime(deadline, "%Y-%m-%d")

    # ----------------- TASK OPERATIONS -----------------
    def edit(self, *, new_title: Optional[str] = None,
             new_description: Optional[str] = None,
             new_status: Optional[str] = None,
             new_deadline: Optional[str] = None):
        """
        Edit task attributes.
        """
        if new_title:
            self.validate_title(new_title)
            self.title = new_title.strip()

        if new_description:
            self.validate_description(new_description)
            self.description = new_description.strip()

        if new_status:
            self.set_status(new_status)

        if new_deadline:
            self.set_deadline(new_deadline)

    def delete_task(self):
        """
        Remove this task from its container project.
        """
        if self.container_project and self in self.container_project.tasks:
            self.container_project.tasks.remove(self)
            self.container_project = None
            return {"status": "success", "message": "Task deleted successfully."}
        return {"status": "error", "message": "Task not found in its project."}

    # ----------------- REPRESENTATION -----------------
    def __str__(self):
        deadline_str = self.deadline.strftime("%Y-%m-%d") if self.deadline else "No deadline"
        return f"Task: {self.title} | Status: {self.status} | Deadline: {deadline_str}"

    def __repr__(self):
        return self.__str__()
