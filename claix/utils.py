import shelve
import subprocess
from pathlib import Path
import rich
from claix.bot import Bot

DEFAULT_INSTRUCTIONS = """Claix exclusively provides Linux CLI command translations in plain text, with no code blocks or additional formatting. When a user's input aligns with Linux CLI commands, Claix responds with the exact command in simple text. If the input is unrelated to Linux CLI commands, Claix replies with a single '.' to maintain focus on its primary role.

This GPT avoids any execution or simulation of CLI commands and does not engage in discussions beyond Linux CLI command translation. Claix's responses are brief and to the point, delivering Linux CLI commands in an unembellished, clear format, ensuring users receive direct and unformatted command syntax for their Linux-related inquiries."""


db_path = Path.home() / '.claix' / 'db'
db_path.parent.mkdir(exist_ok=True)



def run_shell_command(command):
    result = subprocess.run(command, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, 
                            text=True, 
                            shell=True)
    return result



def get_assistant_id(assistant: str = "default"):
    with shelve.open(str(db_path)) as db:
        try:
            return db["assistants"][assistant]["id"]
        except KeyError:
            return None


def set_assistant_id(assistant_id, assistant="default"):
    with shelve.open(str(db_path)) as db:
        assistants = db.get("assistants", {})
        default = assistants.get(assistant)
        if default:
            db["assistants"][assistant]["id"] = assistant_id
        else:
            db["assistants"] = {assistant: {"id": assistant_id}}
    return assistant_id


def get_or_create_default_assistant_id():
    assistant_id = get_assistant_id()
    if not assistant_id:
        assistant = Bot.create_assistant(
            name="default",
            instructions=DEFAULT_INSTRUCTIONS,
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
        thread = Bot.create_thread()
        thread_id = set_thread_id(thread.id, thread="default")
    return thread_id



def simulate_clear(console: rich.console.Console):
    """
    Simulates clearing the console by printing enough new lines to push old content out of view,
    then moves the cursor back to the top of the console window.
    """
    height = console.size.height
    print("\n" * height, end='')  # Print newlines to push content out of view
    print(f"\033[{height}A", end='')  # Move the cursor back up to the top of the console window