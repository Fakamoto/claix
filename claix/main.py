from enum import Enum, auto
import typer
from claix.ai import Claix, ClaixCommand
from claix.typer_utils import (
    version_callback,
    instructions_callback,
    openai_api_key_callback,
)
from claix.utils import (
    get_or_create_default_assistant_id,
    get_or_create_default_thread_id,
    ask_user_if_run_revise_or_exit,
    run_shell_command,
    simulate_clear,
    Action,
)
from rich.console import Console

app = typer.Typer(name="claix", no_args_is_help=True, add_completion=False)


class State(Enum):
    PROCESS_INSTRUCTIONS = auto()
    GATHER_REVISION = auto()
    PRINT_EXPLANATION = auto()
    USER_DECISION = auto()
    RUN_COMMAND = auto()
    HANDLE_FAILURE = auto()
    EXIT = auto()


@app.command(help="Turns your instructions into CLI commands ready to execute.")
def main(
    initial_instructions: list[str] = typer.Argument(
        None,
        callback=instructions_callback,
        help="The instructions that you want to execute.",
    ),
    show_version: bool = typer.Option(
        None,
        "--version",
        "-v",
        callback=version_callback,
        is_eager=True,
        help="Show the version and exit.",
    ),
    openai_api_key: str = typer.Option(
        None,
        hidden=True,
        callback=openai_api_key_callback,
        envvar="OPENAI_API_KEY",
        help="The OpenAI API key.",
    ),
):
    instructions = " ".join(initial_instructions)
    error_iterations = 0

    assistant_id = get_or_create_default_assistant_id()
    thread_id = get_or_create_default_thread_id()

    console = Console()
    claix = Claix(assistant_id, thread_id)
    state = State.PROCESS_INSTRUCTIONS

    start = True
    while state != State.EXIT:
        if state == State.PROCESS_INSTRUCTIONS:
            with console.status("Thinking...", spinner="dots"):
                claix_command: ClaixCommand = claix(instructions)

            if not claix_command.is_command:
                typer.echo(
                    typer.style(
                        "Claix Response: I don't know how to solve this problem, exiting",
                        fg=typer.colors.RED,
                        bold=True,
                    )
                )
                state = State.EXIT
            else:
                typer.echo(
                    typer.style("Proposed Command:", fg=typer.colors.GREEN, bold=True)
                )
                typer.echo(f"{claix_command.command}\n")
                state = State.USER_DECISION

        elif state == State.USER_DECISION:
            user_action = ask_user_if_run_revise_or_exit()
            #simulate_clear(console)
            if user_action == Action.EXIT:
                state = State.EXIT
            elif user_action == Action.REVISE:
                state = State.GATHER_REVISION
            elif user_action == Action.EXPLAIN:
                state = State.PRINT_EXPLANATION
            elif user_action == Action.RUN:
                state = State.RUN_COMMAND

        elif state == State.GATHER_REVISION:
            instructions = typer.prompt("Enter your revision")
            state = State.PROCESS_INSTRUCTIONS

        elif state == State.PRINT_EXPLANATION:
            typer.echo(
                typer.style("Explanation:", fg=typer.colors.BLUE, bold=True)
            )
            typer.echo(f"{claix_command.explanation}\n")
            state = State.USER_DECISION

        elif state == State.RUN_COMMAND:
            with console.status("Running command...", spinner="dots"):
                command_run_result = run_shell_command(claix_command.command)
            if command_run_result.returncode == 0:
                if command_run_result.stdout:
                    typer.echo(typer.style("Output:", fg=typer.colors.BLUE, bold=True))
                    typer.echo(command_run_result.stdout)
                else:
                    typer.echo(
                        typer.style("No output.", fg=typer.colors.BLUE, bold=True)
                    )
                state = State.EXIT
            else:
                typer.echo(
                    typer.style("Command failed...", fg=typer.colors.RED, bold=True)
                )
                state = State.HANDLE_FAILURE
                error_iterations = 0

        elif state == State.HANDLE_FAILURE:
            if error_iterations > 2:
                typer.echo(
                    typer.style(
                        "Too many errors, exiting", fg=typer.colors.RED, bold=True
                    )
                )
                state = State.EXIT
                break
            with console.status("Thinking", spinner="dots"):
                claix_command: ClaixCommand = claix.get_fixed_command(
                    instructions, claix_command.command, command_run_result
                )
            if not claix_command.is_command:
                typer.echo(
                    typer.style(
                        "Claix Response: I don't know how to solve this problem, exiting",
                        fg=typer.colors.RED,
                        bold=True,
                    )
                )
                state = State.EXIT
            else:
                typer.echo(
                    typer.style("Proposed Solution:", fg=typer.colors.GREEN, bold=True)
                )
                typer.echo(f"{claix_command.command}\n")

                user_action = ask_user_if_run_revise_or_exit()
                #simulate_clear(console)
                if user_action == Action.EXIT:
                    state = State.EXIT
                elif user_action == Action.REVISE:
                    state = State.GATHER_REVISION
                elif user_action == Action.EXPLAIN:
                    state = State.PRINT_EXPLANATION
                elif user_action == Action.RUN:
                    state = State.RUN_COMMAND
                    error_iterations += 1


if __name__ == "__main__":
    app()
