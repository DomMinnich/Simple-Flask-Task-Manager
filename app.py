#Simple To-Do List / Task Manager app using Flask


#  Import Flask and run with: python app.py

#
# Imports and Global Variables
# Functions A --> Z
# Routes    A --> Z
#

# Importing the required modules
from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import json

app = Flask(__name__)

# Global Variables
tasks = []
logs = []

# Functions
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return {"__datetime__": obj.isoformat()}
        return super(DateTimeEncoder, self).default(obj)

# Custom JSON decoder to convert datetime strings to datetime objects
def json_datetime_decoder(obj):
    if "__datetime__" in obj:
        return datetime.fromisoformat(obj["__datetime__"])
    return obj

def json_datetime_hook(dct):
    for key, value in dct.items():
        if isinstance(value, str) and key.endswith("_at"):
            try:
                dct[key] = datetime.fromisoformat(value)
            except ValueError:
                pass
    return dct

# Load data from data.json
def load_data():
    global tasks, logs
    try:
        with open("data.json", "r") as file:
            data = json.load(file, object_hook=json_datetime_decoder)
            tasks = data.get("tasks", [])
            logs = data.get("logs", [])
    except FileNotFoundError:
        pass

# Save data to data.json
def save_data():
    with open("data.json", "w") as file:
        json.dump({"tasks": tasks, "logs": logs}, file, cls=DateTimeEncoder)

# Routes
@app.route("/")
def index():
    load_data()
    current_time = datetime.now()
    return render_template("index.html", tasks=tasks, logs=logs, now=current_time)

# Add a task route 
@app.route("/add_task", methods=["POST"])
def add_task():
    title = request.form.get("title")
    
    if title:
        new_task = {
            "title": title,
            "created_at": datetime.now(),
            "completed": False
        }
        tasks.append(new_task)
        logs.append(f"Task '{title}' added at {datetime.now()}")
        save_data()

    return redirect(url_for("index"))

# Complete a task route
@app.route("/complete_task/<int:task_index>")
def complete_task(task_index):
    if 0 <= task_index < len(tasks):
        tasks[task_index]["completed"] = True
        tasks[task_index]["completed_at"] = datetime.now()
        logs.append(f"Task '{tasks[task_index]['title']}' completed at {datetime.now()}")
        save_data()

    return redirect(url_for("index"))

# Delete a task route
@app.route("/delete_task/<int:task_index>")
def delete_task(task_index):
    if 0 <= task_index < len(tasks):
        deleted_title = tasks[task_index]["title"]
        del tasks[task_index]
        logs.append(f"Task '{deleted_title}' deleted at {datetime.now()}")
        save_data()

    return redirect(url_for("index"))

# Highlight logs within log list route
@app.route("/highlight_logs/<string:task_title>")
def highlight_logs(task_title):
    # Highlight logs that contain the task title
    highlighted_logs = [log if task_title in log else f'<strong>{log}</strong>' for log in logs]
    return render_template("index.html", tasks=tasks, logs=highlighted_logs, now=datetime.now())

# Reset a task route
@app.route("/reset_task/<int:task_index>")
def reset_task(task_index):
    if 0 <= task_index < len(tasks):
        tasks[task_index]["completed"] = False
        logs.append(f"Task '{tasks[task_index]['title']}' reset at {datetime.now()}")
        
        # If the task was previously completed, update last_completed_at
        if "completed_at" in tasks[task_index]:
            tasks[task_index]["last_completed_at"] = tasks[task_index]["completed_at"]
            del tasks[task_index]["completed_at"]
            
        save_data()

    return redirect(url_for("index"))

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
