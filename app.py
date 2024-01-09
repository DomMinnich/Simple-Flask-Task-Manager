from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import json

app = Flask(__name__)

tasks = []
logs = []

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return {"__datetime__": obj.isoformat()}
        return super(DateTimeEncoder, self).default(obj)


def save_data():
    with open("data.json", "w") as file:
        json.dump({"tasks": tasks, "logs": logs}, file, cls=DateTimeEncoder)

def load_data():
    global tasks, logs
    try:
        with open("data.json", "r") as file:
            data = json.load(file, object_hook=json_datetime_decoder)
            tasks = data.get("tasks", [])
            logs = data.get("logs", [])
    except FileNotFoundError:
        pass


def json_datetime_hook(dct):
    for key, value in dct.items():
        if isinstance(value, str) and key.endswith("_at"):
            try:
                dct[key] = datetime.fromisoformat(value)
            except ValueError:
                pass
    return dct

def json_datetime_decoder(obj):
    if "__datetime__" in obj:
        return datetime.fromisoformat(obj["__datetime__"])
    return obj


@app.route("/")
def index():
    load_data()
    current_time = datetime.now()
    return render_template("index.html", tasks=tasks, logs=logs, now=current_time)


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

@app.route("/delete_task/<int:task_index>")
def delete_task(task_index):
    if 0 <= task_index < len(tasks):
        deleted_title = tasks[task_index]["title"]
        del tasks[task_index]
        logs.append(f"Task '{deleted_title}' deleted at {datetime.now()}")
        save_data()

    return redirect(url_for("index"))


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


@app.route("/highlight_logs/<string:task_title>")
def highlight_logs(task_title):
    # Highlight logs that contain the task title
    highlighted_logs = [log if task_title in log else f'<strong>{log}</strong>' for log in logs]
    return render_template("index.html", tasks=tasks, logs=highlighted_logs, now=datetime.now())


@app.route("/complete_task/<int:task_index>")
def complete_task(task_index):
    if 0 <= task_index < len(tasks):
        tasks[task_index]["completed"] = True
        tasks[task_index]["completed_at"] = datetime.now()
        logs.append(f"Task '{tasks[task_index]['title']}' completed at {datetime.now()}")
        save_data()

    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
