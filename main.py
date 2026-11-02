
import json
from pathlib import Path
from datetime import datetime, date
from difflib import get_close_matches

DATA_FILE = Path(__file__).parent / "selenova_memory.json"

def load_data():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except (json.JSONDecodeError, OSError):
            print("Memory file could not be read.")

    return {
        "memories": [],
        "goals": [],
        "tasks": [],
        "journal": []
    }

data = load_data()

def save_data():
    temp_file = DATA_FILE.with_suffix(".tmp")

    with open(temp_file, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4, ensure_ascii=False)

    temp_file.replace(DATA_FILE)


# adaptive memory

def remember(category, information):
    entry = {
        "category": category,
        "information": information,
        "created": datetime.now().isoformat(timespec="seconds")
    }

    data["memories"].append(entry)
    save_data()

    print("SELENOVA: Information stored in my memory.")


def recall(keyword):
    results = [
        item for item in data["memories"]
        if keyword.lower() in (
            item["category"] + " " + item["information"]
        ).lower()
    ]

    if not results:
        print("SELENOVA: No matching memories found.")
        return

    print("\n--- MEMORY RETRIEVAL ---")

    for item in results:
        print(f"[{item['category']}] {item['information']}")


# goal

def add_goal(goal):
    data["goals"].append({
        "goal": goal,
        "created": date.today().isoformat(),
        "completed": False
    })

    save_data()
    print("SELENOVA: New objective registered.")


def add_task(priority, due_date, description):
    if priority not in ["high", "medium", "low"]:
        print("Use priority: high, medium or low.")
        return

    try:
        due = date.fromisoformat(due_date)
    except ValueError:
        print("Date format must be YYYY-MM-DD.")
        return

    if due < date.today():
        print("Please provide a future date.")
        return

    data["tasks"].append({
        "description": description,
        "priority": priority,
        "due": due.isoformat(),
        "completed": False,
        "created": datetime.now().isoformat(timespec="seconds")
    })

    save_data()
    print("SELENOVA: Task registered and prioritized.")


def calculate_task_score(task):
    priority_score = {
        "high": 30,
        "medium": 20,
        "low": 10
    }

    days_left = (
        date.fromisoformat(task["due"]) - date.today()
    ).days

    urgency_score = max(0, 30 - days_left * 2)

    return priority_score[task["priority"]] + urgency_score


def generate_plan():
    pending = [
        task for task in data["tasks"]
        if not task["completed"]
    ]

    pending.sort(key=calculate_task_score, reverse=True)

    print("\n--- SELENOVA'S PRIORITY ANALYSIS ---")

    if not pending:
        print("No pending tasks. Time to define a new objective!")
        return

    for index, task in enumerate(pending, 1):
        score = calculate_task_score(task)

        print(f"\n{index}. {task['description']}")
        print(f"   Priority: {task['priority'].upper()}")
        print(f"   Deadline: {task['due']}")
        print(f"   Intelligence score: {score}")

    print("\nSELENOVA: Start with the highest-scoring task.")


# daily

def daily_briefing():
    print("\n========== SELENOVA DAILY BRIEFING ==========")

    print("Date:", date.today().strftime("%d %B %Y"))

    active_goals = [
        goal for goal in data["goals"]
        if not goal["completed"]
    ]

    completed_tasks = [
        task for task in data["tasks"]
        if task["completed"]
    ]

    pending_tasks = [
        task for task in data["tasks"]
        if not task["completed"]
    ]

    overdue = [
        task for task in pending_tasks
        if date.fromisoformat(task["due"]) < date.today()
    ]

    print("\nACTIVE OBJECTIVES:", len(active_goals))
    print("PENDING TASKS:", len(pending_tasks))
    print("COMPLETED TASKS:", len(completed_tasks))
    print("OVERDUE TASKS:", len(overdue))

    if overdue:
        print("\nAttention: You have overdue tasks!")

    generate_plan()

    print("\n=============================================")


# decision

def record_learning(note):
    data["journal"].append({
        "note": note,
        "date": datetime.now().isoformat(timespec="seconds")
    })

    save_data()
    print("SELENOVA: Experience recorded for future reference.")


def review_learning(keyword):
    results = [
        item for item in data["journal"]
        if keyword.lower() in item["note"].lower()
    ]

    if not results:
        print("SELENOVA: No related experiences found.")
        return

    print("\n--- PREVIOUS EXPERIENCES ---")

    for item in results:
        print(item["date"], "-", item["note"])


# commands

COMMANDS = [
    "remember",
    "recall",
    "goal",
    "task",
    "plan",
    "brief",
    "reflect",
    "review",
    "complete",
    "help",
    "exit"
]


def understand_command(user_input):
    command = user_input.strip().lower()

    if not command:
        return None

    for known_command in COMMANDS:
        if command == known_command or command.startswith(
            known_command + " "
        ):
            return known_command

    match = get_close_matches(
        command.split()[0],
        COMMANDS,
        n=1,
        cutoff=0.75
    )

    if match:
        print(
            f"SELENOVA: Did you mean '{match[0]}'?"
        )
    else:
        print(
            "SELENOVA: I don't understand that instruction yet."
        )

    return None


# ---------- COMMAND EXECUTION ----------

def execute(command, user_input):

    content = user_input[len(command):].strip()

    if command == "remember":
        if ":" not in content:
            print("Format: remember category: information")
            return

        category, information = content.split(":", 1)
        remember(category.strip(), information.strip())

    elif command == "recall":
        recall(content)

    elif command == "goal":
        add_goal(content)

    elif command == "task":
        parts = content.split(maxsplit=2)

        if len(parts) != 3:
            print("Format: task priority YYYY-MM-DD description")
            return

        add_task(parts[0].lower(), parts[1], parts[2])

    elif command == "plan":
        generate_plan()

    elif command == "brief":
        daily_briefing()

    elif command == "reflect":
        record_learning(content)

    elif command == "review":
        review_learning(content)

    elif command == "complete":
        for task in data["tasks"]:
            if (
                content.lower() == task["description"].lower()
                and not task["completed"]
            ):
                task["completed"] = True
                save_data()
                print("SELENOVA: Task marked complete.")
                return

        print("SELENOVA: Matching pending task not found.")

    elif command == "help":
        show_commands()


def show_commands():
    print("""
SELENOVA COMMAND CENTER

MEMORY:
remember category: information
recall keyword

GOALS:
goal your long-term objective

TASKS:
task high 2026-11-05 task description
plan
complete exact task description

INTELLIGENCE:
brief
reflect something you learned
review keyword

SYSTEM:
help
exit

""")

def start_selenova():

    print("""
  ███████╗███████╗██╗     ███████╗███╗   ██╗
  ██╔════╝██╔════╝██║     ██╔════╝████╗  ██║
  ███████╗█████╗  ██║     █████╗  ██╔██╗ ██║
  ╚════██║██╔══╝  ██║     ██╔══╝  ██║╚██╗██║
  ███████║███████╗███████╗███████╗██║ ╚████║
  ╚══════╝╚══════╝╚══════╝╚══════╝╚═╝  ╚═══╝

       PERSONAL INTELLIGENCE SYSTEM
                 VERSION 0.1
    """)

    print("SELENOVA: Systems initialized.")
    print("SELENOVA: Your personal intelligence system is ready.")

    show_commands()

    while True:
        user_input = input("\nYOU > ").strip()

        command = understand_command(user_input)

        if command == "exit":
            save_data()
            print("SELENOVA: Memory secured. Until next time.")
            break

        if command:
            execute(command, user_input)


if __name__ == "__main__":
    start_selenova()
