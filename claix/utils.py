import os
import shelve
import subprocess
from pathlib import Path
from enum import Enum, auto
import rich
import inquirer
from claix.ai import Claix, ClaixCommand
import dbm

USER_OS = "Windows" if os.name == "nt" else "Posix"

DEFAULT_INSTRUCTIONS = f"""
Claix exclusively provides CLI command translations in plain text for any OS but specially {USER_OS}, with no code blocks or additional formatting. When a user's input aligns with {USER_OS} CLI commands, Claix responds with the exact command in simple text followed by a brief explanation of its function in simple text. If the input is unrelated to {USER_OS} CLI commands, Claix replies with a single '.' to maintain focus on its primary role.

This GPT avoids any execution or simulation of CLI commands and does not engage in discussions beyond {USER_OS} CLI command translation and explanation. Claix's responses are concise, delivering {USER_OS} CLI commands along with succinct explanations in an unembellished, clear format, ensuring users receive direct and unformatted command syntax and understanding for their {USER_OS}-related inquiries.
"""

db_path = Path.home() / ".claix" / "db"
db_path.parent.mkdir(exist_ok=True)


class Action(Enum):
    RUN = auto()
    REVISE = auto()
    EXPLAIN = auto()
    EXIT = auto()


    def __str__(self):
        # Return the string representation for the prompt
        emojis = {
            Action.RUN: "\U00002705 Run Command",
            Action.REVISE: "\U0001F4DD Revise Command",
            Action.EXPLAIN: "\U0001F4D6 Explain Command",
            Action.EXIT: "\U0000274C Exit",
        }
        return emojis[self]


def ask_user_if_run_revise_or_exit() -> Action:
    questions = [
        inquirer.List(
            "action",
            message="Choose an action",
            choices=list(Action),
        ),
    ]
    action_response = inquirer.prompt(questions, raise_keyboard_interrupt=True)[
        "action"
    ]

    return Action(action_response)


def run_shell_command(command):
    command_run_result = subprocess.run(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=True
    )
    return command_run_result


def get_assistant_id(assistant: str = "default"):
    try:
        with shelve.open(str(db_path)) as db:
            try:
                return db["assistants"][assistant]["id"]
            except KeyError:
                return None
    except dbm.error:
        # If the database can't be opened, we'll create a new one
        return None


def set_assistant_id(assistant_id, assistant="default"):
    try:
        with shelve.open(str(db_path)) as db:
            assistants = db.get("assistants", {})
            default = assistants.get(assistant)
            if default:
                db["assistants"][assistant]["id"] = assistant_id
            else:
                db["assistants"] = {assistant: {"id": assistant_id}}
        return assistant_id
    except dbm.error:
        # If we can't open or create the database, we'll just return the assistant_id
        # This means we'll create a new assistant each time, but it's better than crashing
        return assistant_id


def get_or_create_default_assistant_id():
    assistant_id = get_assistant_id()
    if not assistant_id:
        assistant = Claix.create_assistant(
            name="default",
            instructions=DEFAULT_INSTRUCTIONS,
            model="gpt-4o-mini",
            tools=[{"type": "code_interpreter"}, {"type": "file_search"}]
        )
        assistant_id = set_assistant_id(assistant.id, assistant="default")
    return assistant_id


def get_thread_id(thread: str = "default"):
    with shelve.open(str(db_path)) as db:
        try:
            return db["threads"][thread]["id"]
        except KeyError:
            return None


def set_thread_id(thread_id, thread="default"):
    with shelve.open(str(db_path)) as db:
        threads = db.get("threads", {})
        default = threads.get(thread)
        if default:
            db["threads"][thread]["id"] = thread_id
        else:
            db["threads"] = {thread: {"id": thread_id}}
    return thread_id


def get_or_create_default_thread_id():
    thread_id = get_thread_id()
    if not thread_id:
        thread = Claix.create_thread()
        thread_id = set_thread_id(thread.id, thread="default")
    return thread_id


def simulate_clear(console: rich.console.Console):
    """
    Simulates clearing the console by printing enough new lines to push old content out of view,
    then moves the cursor back to the top of the console window.
    """
    height = console.size.height
    print("\n" * height, end="")  # Print newlines to push content out of view
    print(
        f"\033[{height}A", end=""
    )  # Move the cursor back up to the top of the console window
