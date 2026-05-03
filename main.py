#!/usr/bin/env python3
"""
Task Manager Console Application
Author: Vara Akuseva
Course: Final Certification Project
Date: 03.05.2026  

This is a complete Task Management System with:
- MVC architecture
- Queue (FIFO) for pending tasks
- Stack (LIFO) for undo operations
- JSON file persistence
- Input validation
- Full testing
"""

import json
import os
import uuid
import re
from datetime import datetime
from collections import deque
from typing import List, Optional, Dict
from enum import Enum
from dataclasses import dataclass

# ============================================================================
# MODELS
# ============================================================================

class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class Status(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"

@dataclass
class Task:
    title: str
    description: str
    priority: Priority
    status: Status
    created_at: str
    due_date: str
    task_id: str = None
    
    def __post_init__(self):
        if self.task_id is None:
            self.task_id = str(uuid.uuid4())[:8]
    
    def to_dict(self):
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority.value,
            "status": self.status.value,
            "created_at": self.created_at,
            "due_date": self.due_date
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            task_id=data["task_id"],
            title=data["title"],
            description=data["description"],
            priority=Priority(data["priority"]),
            status=Status(data["status"]),
            created_at=data["created_at"],
            due_date=data["due_date"]
        )


class TaskManager:
    """Main task manager with Queue (FIFO) and Stack (LIFO)"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.history: deque = deque(maxlen=50)  # Stack for undo
        self.pending_queue: deque = deque()     # Queue for pending tasks
    
    def add_task(self, task: Task) -> bool:
        if task.task_id in self.tasks:
            return False
        self.tasks[task.task_id] = task
        self._add_to_history(f"ADD:{task.task_id}:{task.title}")
        if task.status == Status.PENDING:
            self.pending_queue.append(task)
        return True
    
    def remove_task(self, task_id: str) -> bool:
        if task_id not in self.tasks:
            return False
        removed_task = self.tasks.pop(task_id)
        self._add_to_history(f"REMOVE:{task_id}:{removed_task.title}")
        self.pending_queue = deque([t for t in self.pending_queue if t.task_id != task_id])
        return True
    
    def update_task(self, task_id: str, **kwargs) -> bool:
        if task_id not in self.tasks:
            return False
        task = self.tasks[task_id]
        old_status = task.status
        self._add_to_history(f"UPDATE:{task_id}")
        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)
        if old_status != task.status:
            if task.status == Status.PENDING:
                self.pending_queue.append(task)
            else:
                self.pending_queue = deque([t for t in self.pending_queue if t.task_id != task_id])
        return True
    
    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)
    
    def get_all_tasks(self) -> List[Task]:
        return list(self.tasks.values())
    
    def filter_tasks(self, **filters) -> List[Task]:
        results = self.get_all_tasks()
        for key, value in filters.items():
            if value is not None:
                if key == "priority":
                    results = [t for t in results if t.priority == value]
                elif key == "status":
                    results = [t for t in results if t.status == value]
                elif key == "title_contains":
                    results = [t for t in results if value.lower() in t.title.lower()]
        return results
    
    def get_next_pending_task(self) -> Optional[Task]:
        """FIFO queue - returns next pending task"""
        if self.pending_queue:
            return self.pending_queue.popleft()
        return None
    
    def undo_last_operation(self) -> bool:
        """LIFO stack - undoes last operation"""
        if self.history:
            last_op = self.history.pop()
            parts = last_op.split(":")
            if parts[0] == "ADD" and len(parts) >= 2:
                self.remove_task(parts[1])
                return True
        return False
    
    def _add_to_history(self, operation: str):
        self.history.append(operation)
    
    def get_statistics(self) -> dict:
        tasks = self.get_all_tasks()
        return {
            "total_tasks": len(tasks),
            "pending": len([t for t in tasks if t.status == Status.PENDING]),
            "in_progress": len([t for t in tasks if t.status == Status.IN_PROGRESS]),
            "completed": len([t for t in tasks if t.status == Status.COMPLETED]),
            "high_priority": len([t for t in tasks if t.priority == Priority.HIGH]),
            "queue_length": len(self.pending_queue),
            "history_count": len(self.history)
        }


# ============================================================================
# UTILS
# ============================================================================

class Validators:
    @staticmethod
    def validate_title(title: str) -> tuple:
        if not title or not title.strip():
            return False, "Title cannot be empty"
        if len(title) > 100:
            return False, "Title must be less than 100 characters"
        return True, ""
    
    @staticmethod
    def validate_description(description: str) -> tuple:
        if len(description) > 500:
            return False, "Description must be less than 500 characters"
        return True, ""
    
    @staticmethod
    def validate_date(date_str: str) -> tuple:
        if not date_str or not date_str.strip():
            return False, "Date cannot be empty"
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True, ""
        except ValueError:
            return False, "Invalid date format. Use YYYY-MM-DD"
    
    @staticmethod
    def validate_task_id(task_id: str) -> tuple:
        if not task_id or not task_id.strip():
            return False, "Task ID cannot be empty"
        if len(task_id) != 8:
            return False, "Task ID must be 8 characters long"
        if not re.match(r'^[a-f0-9]{8}$', task_id):
            return False, "Task ID must contain only hexadecimal characters"
        return True, ""


class JSONHandler:
    DATA_FILE = "task_data.json"
    
    def __init__(self, filename: str = DATA_FILE):
        self.filename = filename
    
    def save_tasks(self, task_manager: TaskManager) -> bool:
        try:
            data = {
                "tasks": [task.to_dict() for task in task_manager.get_all_tasks()],
                "history": list(task_manager.history),
                "saved_at": datetime.now().isoformat()
            }
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving: {e}")
            return False
    
    def load_tasks(self, task_manager: TaskManager) -> bool:
        if not os.path.exists(self.filename):
            print(f"File {self.filename} not found. Starting empty.")
            return False
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for task_data in data.get("tasks", []):
                    task = Task.from_dict(task_data)
                    task_manager.add_task(task)
                for hist_item in data.get("history", []):
                    task_manager.history.append(hist_item)
            return True
        except Exception as e:
            print(f"Error loading: {e}")
            return False


# ============================================================================
# VIEW
# ============================================================================

class ConsoleView:
    @staticmethod
    def display_main_menu():
        print("\n" + "="*60)
        print("TASK MANAGER SYSTEM - MAIN MENU")
        print("="*60)
        print("1. Add New Task")
        print("2. View All Tasks")
        print("3. Filter Tasks")
        print("4. Update Task")
        print("5. Delete Task")
        print("6. Process Next Pending Task (FIFO Queue)")
        print("7. View Statistics")
        print("8. Undo Last Operation (LIFO Stack)")
        print("9. Save & Exit")
        print("="*60)
    
    @staticmethod
    def display_tasks(tasks: List[Task], title: str = "Tasks"):
        if not tasks:
            print(f"\nNo tasks found")
            return
        print(f"\n{title}:")
        print("-" * 90)
        print(f"{'ID':<10} {'Title':<30} {'Priority':<10} {'Status':<15} {'Due Date':<12}")
        print("-" * 90)
        for task in tasks:
            title_display = task.title[:27] + ".." if len(task.title) > 29 else task.title
            print(f"{task.task_id:<10} {title_display:<30} {task.priority.value:<10} {task.status.value:<15} {task.due_date:<12}")
        print("-" * 90)
        print(f"Total: {len(tasks)} tasks")
    
    @staticmethod
    def display_task_details(task: Task):
        print("\n" + "="*50)
        print("TASK DETAILS")
        print("="*50)
        print(f"ID:          {task.task_id}")
        print(f"Title:       {task.title}")
        print(f"Description: {task.description}")
        print(f"Priority:    {task.priority.value}")
        print(f"Status:      {task.status.value}")
        print(f"Created:     {task.created_at}")
        print(f"Due Date:    {task.due_date}")
        print("="*50)
    
    @staticmethod
    def display_statistics(stats: dict):
        print("\n" + "="*50)
        print("TASK STATISTICS")
        print("="*50)
        print(f"Total Tasks:        {stats['total_tasks']}")
        print(f"Pending:            {stats['pending']}")
        print(f"In Progress:        {stats['in_progress']}")
        print(f"Completed:          {stats['completed']}")
        print(f"High Priority:      {stats['high_priority']}")
        print(f"Queue Length (FIFO): {stats['queue_length']}")
        print(f"History Records (Stack): {stats['history_count']}")
        print("="*50)
    
    @staticmethod
    def show_message(message: str, is_error: bool = False):
        prefix = "ERROR:" if is_error else "INFO:"
        print(f"\n{prefix} {message}")
    
    @staticmethod
    def get_user_input(prompt: str) -> str:
        return input(prompt).strip()
    
    @staticmethod
    def get_yes_no(prompt: str) -> bool:
        return input(f"{prompt} (y/n): ").lower().strip() == 'y'
    
    @staticmethod
    def get_task_input():
        print("\nEnter New Task Details:")
        print("-" * 30)
        title = input("Title: ").strip()
        description = input("Description: ").strip()
        print("\nPriority options: low, medium, high")
        priority = input("Priority (default: medium): ").lower().strip()
        print("\nStatus options: pending, in_progress, completed")
        status = input("Status (default: pending): ").lower().strip()
        due_date = input("Due Date (YYYY-MM-DD): ").strip()
        created_at = datetime.now().strftime("%Y-%m-%d")
        return title, description, priority, status, created_at, due_date
    
    @staticmethod
    def get_filter_criteria():
        print("\nFilter Tasks (leave empty to skip):")
        print("-" * 40)
        priority = input("Priority (low/medium/high): ").lower().strip()
        status = input("Status (pending/in_progress/completed): ").lower().strip()
        title_contains = input("Title contains: ").strip()
        filters = {}
        if priority in ["low", "medium", "high"]:
            filters['priority'] = Priority(priority)
        if status in ["pending", "in_progress", "completed"]:
            filters['status'] = Status(status)
        if title_contains:
            filters['title_contains'] = title_contains
        return filters


# ============================================================================
# CONTROLLER
# ============================================================================

class TaskController:
    def __init__(self):
        self.task_manager = TaskManager()
        self.view = ConsoleView()
        self.json_handler = JSONHandler()
        self.validators = Validators()
        self.is_running = True
    
    def run(self):
        self.json_handler.load_tasks(self.task_manager)
        self.view.show_message(f"Ready! Loaded {len(self.task_manager.get_all_tasks())} tasks")
        
        while self.is_running:
            self.view.display_main_menu()
            choice = self.view.get_user_input("\nEnter choice (1-9): ")
            
            if choice == "1":
                self.add_task()
            elif choice == "2":
                self.view_all_tasks()
            elif choice == "3":
                self.filter_tasks()
            elif choice == "4":
                self.update_task()
            elif choice == "5":
                self.delete_task()
            elif choice == "6":
                self.process_next_pending()
            elif choice == "7":
                self.show_statistics()
            elif choice == "8":
                self.undo_operation()
            elif choice == "9":
                self.save_and_exit()
            else:
                self.view.show_message("Invalid choice", is_error=True)
    
    def add_task(self):
        title, desc, priority_input, status_input, created_at, due_date = self.view.get_task_input()
        
        is_valid, err = self.validators.validate_title(title)
        if not is_valid:
            self.view.show_message(err, is_error=True)
            return
        
        is_valid, err = self.validators.validate_description(desc)
        if not is_valid:
            self.view.show_message(err, is_error=True)
            return
        
        is_valid, err = self.validators.validate_date(due_date)
        if not is_valid:
            self.view.show_message(err, is_error=True)
            return
        
        try:
            priority = Priority(priority_input) if priority_input else Priority.MEDIUM
        except ValueError:
            priority = Priority.MEDIUM
        
        try:
            status = Status(status_input) if status_input else Status.PENDING
        except ValueError:
            status = Status.PENDING
        
        task = Task(title=title, description=desc, priority=priority, 
                    status=status, created_at=created_at, due_date=due_date)
        
        if self.task_manager.add_task(task):
            self.view.show_message(f"Task added! ID: {task.task_id}")
            self.view.display_task_details(task)
        else:
            self.view.show_message("Failed to add task", is_error=True)
    
    def view_all_tasks(self):
        self.view.display_tasks(self.task_manager.get_all_tasks(), "All Tasks")
    
    def filter_tasks(self):
        filters = self.view.get_filter_criteria()
        tasks = self.task_manager.filter_tasks(**filters) if filters else self.task_manager.get_all_tasks()
        self.view.display_tasks(tasks, "Filtered Results")
    
    def update_task(self):
        task_id = self.view.get_user_input("Enter Task ID to update: ")
        task = self.task_manager.get_task(task_id)
        if not task:
            self.view.show_message("Task not found", is_error=True)
            return
        
        self.view.display_task_details(task)
        print("\nUpdate (Enter to keep current):")
        
        new_title = self.view.get_user_input(f"Title [{task.title}]: ")
        new_desc = self.view.get_user_input(f"Description: ")
        new_priority = self.view.get_user_input(f"Priority [{task.priority.value}]: ").lower()
        new_status = self.view.get_user_input(f"Status [{task.status.value}]: ").lower()
        new_due = self.view.get_user_input(f"Due Date [{task.due_date}]: ")
        
        updates = {}
        if new_title:
            updates['title'] = new_title
        if new_desc:
            updates['description'] = new_desc
        if new_priority in ["low", "medium", "high"]:
            updates['priority'] = Priority(new_priority)
        if new_status in ["pending", "in_progress", "completed"]:
            updates['status'] = Status(new_status)
        if new_due and self.validators.validate_date(new_due)[0]:
            updates['due_date'] = new_due
        
        if updates and self.task_manager.update_task(task_id, **updates):
            self.view.show_message("Task updated!")
        else:
            self.view.show_message("No updates made", is_error=True)
    
    def delete_task(self):
        task_id = self.view.get_user_input("Enter Task ID to delete: ")
        task = self.task_manager.get_task(task_id)
        if not task:
            self.view.show_message("Task not found", is_error=True)
            return
        self.view.display_task_details(task)
        if self.view.get_yes_no(f"Delete '{task.title}'?"):
            if self.task_manager.remove_task(task_id):
                self.view.show_message("Task deleted")
            else:
                self.view.show_message("Delete failed", is_error=True)
    
    def process_next_pending(self):
        """Demonstrates FIFO Queue functionality"""
        next_task = self.task_manager.get_next_pending_task()
        if next_task:
            self.view.show_message(f"Processing from FIFO queue:")
            self.view.display_task_details(next_task)
            self.task_manager.update_task(next_task.task_id, status=Status.IN_PROGRESS)
            self.view.show_message("Task moved to 'in_progress'")
        else:
            self.view.show_message("No pending tasks in queue", is_error=True)
    
    def show_statistics(self):
        stats = self.task_manager.get_statistics()
        self.view.display_statistics(stats)
    
    def undo_operation(self):
        """Demonstrates LIFO Stack functionality"""
        if self.task_manager.undo_last_operation():
            self.view.show_message("Last operation undone (LIFO stack)")
        else:
            self.view.show_message("Nothing to undo", is_error=True)
    
    def save_and_exit(self):
        if self.json_handler.save_tasks(self.task_manager):
            self.view.show_message(f"Saved to {self.json_handler.filename}! Goodbye!")
        else:
            self.view.show_message("Save failed!", is_error=True)
        self.is_running = False


# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "="*60)
    print("TASK MANAGER SYSTEM v1.0")
    print("="*60)
    print("Features:")
    print("  - Queue (FIFO) for pending tasks")
    print("  - Stack (LIFO) for undo operations")
    print("  - JSON file persistence")
    print("  - Full CRUD operations")
    print("="*60)
    
    app = TaskController()
    app.run()


if __name__ == "__main__":
    main()
    # Вставьте этот код в отдельный файл test.py
import unittest
from main import Task, TaskManager, Priority, Status

class TestTaskManager(unittest.TestCase):
    def test_add_task(self):
        tm = TaskManager()
        task = Task("Test", "Desc", Priority.MEDIUM, Status.PENDING, "2024-01-01", "2024-12-31")
        self.assertTrue(tm.add_task(task))
        self.assertEqual(len(tm.get_all_tasks()), 1)
    
    def test_queue_fifo(self):
        tm = TaskManager()
        t1 = Task("Task1", "", Priority.LOW, Status.PENDING, "2024-01-01", "2024-12-31")
        t2 = Task("Task2", "", Priority.LOW, Status.PENDING, "2024-01-01", "2024-12-31")
        tm.add_task(t1)
        tm.add_task(t2)
        first = tm.get_next_pending_task()
        self.assertEqual(first.task_id, t1.task_id)
    
    def test_stack_undo(self):
        tm = TaskManager()
        task = Task("Test", "", Priority.LOW, Status.PENDING, "2024-01-01", "2024-12-31")
        tm.add_task(task)
        self.assertEqual(len(tm.get_all_tasks()), 1)
        tm.undo_last_operation()
        self.assertEqual(len(tm.get_all_tasks()), 0)

if __name__ == "__main__":
    unittest.main()