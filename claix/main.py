# src/main.py
from typing import Literal
from claix import __version__
from claix.bot import Bot
from claix.utils import get_or_create_default_assistant_id, get_or_create_default_thread_id, run_shell_command
from enum import Enum, auto
import inquirer
import typer

app = typer.Typer(name="claix", no_args_is_help=True, add_completion=False)



class Action(Enum):
    RUN = auto()
    REVISE = auto()
    EXIT = auto()

    def __str__(self):
        # Return the string representation for the prompt
        emojis = {
            Action.RUN: "\U00002705 Run Command",
            Action.REVISE: "\U0001F4DD Revise Command",
            Action.EXIT: "\U0000274C Exit",
        }
        return emojis[self]


def prompt_action() -> Action:
    questions = [
        inquirer.List('action',
                      message="Choose an action",
                      choices=list(Action),
                      ),
    ]
    action_response = inquirer.prompt(questions, raise_keyboard_interrupt=True)['action']
    return action_response

# Version callback
def version_callback(show_version: bool):
    if show_version:
        typer.echo(__version__)
        raise typer.Exit()

@app.command(help="Turns your instructions into CLI commands ready to execute.")
def main(instructions: list[str] = typer.Argument(None, help="The instructions that you want to execute. Pass them as a list of strings."),
         show_version: bool = typer.Option(None, "--version", "-v", callback=version_callback, is_eager=True, help="Show the version and exit."),
         ):
    if not instructions:
        typer.echo(typer.style("Error:", fg=typer.colors.RED, bold=True))
        typer.echo("No instructions provided. Claix needs a set of instructions to generate commands.\n")
        typer.echo(typer.style("Example Usage:", fg=typer.colors.BLUE, bold=True))
        typer.echo("claix list all docker containers\nclaix show me active network interfaces\n")
        return

    instructions_str = " ".join(instructions)

    assistant_id = get_or_create_default_assistant_id()
    thread_id = get_or_create_default_thread_id()

    bot = Bot(assistant_id, thread_id)
    
    proposed_command = bot(instructions_str)
    if proposed_command == ".":
        typer.echo(typer.style("Claix Response:", fg=typer.colors.RED, bold=True))
        typer.echo("I don't know how to solve this problem, exiting\n")
        return

    typer.echo(typer.style("Proposed Command:", fg=typer.colors.GREEN, bold=True))
    typer.echo(f"{proposed_command}\n")
    
    user_action = prompt_action()

    if user_action == Action.EXIT:
        typer.echo("Exiting Claix.\n")
        return
    
    elif user_action == Action.REVISE:
        # Implement revise command logic
        typer.echo("Revision needed for the command.\n")
        return

    elif user_action == Action.RUN:
        result = run_shell_command(proposed_command)
        error_iterations = 0

        while result.returncode != 0:
            if error_iterations > 2:
                typer.echo(typer.style("Error:", fg=typer.colors.RED, bold=True))
                typer.echo("Too many errors, exiting\n")
                break

            typer.echo(typer.style(f"Error iteration {error_iterations}:", fg=typer.colors.RED))
            typer.echo(f"{result.stderr}\n")

            error_prompt = (
                f"I want to: '{instructions_str}'\n"
                f"I tried '{proposed_command}'\n"
                f"but got this error: '{result.stderr}'\n\n"
                f"Having this error in mind, fix my original command of '{proposed_command}' "
                f"or give me a new command to solve: '{instructions_str}'"
            )
            
            proposed_solution = bot(error_prompt)

            if proposed_solution == ".":
                typer.echo(typer.style("Claix Response:", fg=typer.colors.RED, bold=True))
                typer.echo("I don't know how to solve this problem, exiting\n")
                return

            typer.echo(typer.style("Proposed Solution:", fg=typer.colors.GREEN, bold=True))
            typer.echo(f"{proposed_solution}\n")

            user_action = prompt_action()

            if user_action == Action.EXIT:
                typer.echo("Exiting Claix.\n")
                return
            
            elif user_action == Action.REVISE:
                # Implement revise command logic
                typer.echo("Revision needed for the command.\n")
                return
            
            elif user_action == Action.RUN:
                result = run_shell_command(proposed_solution)
                error_iterations += 1

        if result.returncode == 0:
            if result.stdout:
                typer.echo(typer.style("Output:", fg=typer.colors.BLUE, bold=True))
                typer.echo(f"{result.stdout}")
            else:
                typer.echo(typer.style("No output.", fg=typer.colors.BLUE, bold=True))

if __name__ == "__main__":
    app()
