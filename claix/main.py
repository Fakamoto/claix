# claix/main.py

from claix.bot import Bot
from claix.typer_utils import (
    version_callback,
    instructions_callback,
    openai_api_key_callback,
)
from claix.utils import (
    Action,
    get_or_create_default_assistant_id,
    get_or_create_default_thread_id,
    prompt_action,
    run_shell_command,
)

from rich.console import Console

import typer

app = typer.Typer(name="claix", no_args_is_help=True, add_completion=False)


@app.command(help="Turns your instructions into CLI commands ready to execute.")
def main(
    instructions: list[str] = typer.Argument(
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
    instructions = " ".join(instructions)
    
    assistant_id = get_or_create_default_assistant_id()
    thread_id = get_or_create_default_thread_id()

    console = Console()

    bot = Bot(assistant_id, thread_id)

    with console.status("Processing...", spinner="dots"):
        # Process instructions and get proposed command
        proposed_command = bot(instructions)
        pass

    if proposed_command == ".":
        typer.echo(typer.style("Claix Response:", fg=typer.colors.RED, bold=True))
        typer.echo("I don't know how to solve this problem, exiting\n")
        return

    # show proposed command
    typer.echo(typer.style("Proposed Command:", fg=typer.colors.GREEN, bold=True))
    typer.echo(f"{proposed_command}\n")

    user_action: Action = prompt_action()

    if user_action == Action.EXIT:
        typer.echo("Exiting Claix.\n")
        return

    elif user_action == Action.REVISE:
        typer.echo(typer.style("Revision Needed:", fg=typer.colors.YELLOW, bold=True))
        typer.echo("Please provide more details or alternative instructions to improve the proposed solution.")
        
        revision_instructions = typer.prompt("Enter your revised instructions: ")
        revised_command = bot.get_revised_command(revision_instructions)
        # chatgpt look here!
        # JUMP TO show proposed command
        # as python doesn't support tail recursion, we need to use a different solution
        # chatgpt look here!
    
    elif user_action == Action.RUN:
        command_run_result = run_shell_command(proposed_command)
        error_iterations = 0
        

        while command_run_result.returncode != 0:
            # COMMAND FAILED

            if error_iterations > 2:
                typer.echo(typer.style("Error:", fg=typer.colors.RED, bold=True))
                typer.echo("Too many errors, exiting\n")
                break

            typer.echo(
                typer.style(f"Error iteration {error_iterations}:", fg=typer.colors.RED)
            )
            typer.echo(f"{command_run_result.stderr}\n")


            proposed_solution: str = bot.get_fixed_command(instructions, proposed_command, command_run_result)

            if proposed_solution == ".":
                typer.echo(
                    typer.style("Claix Response:", fg=typer.colors.RED, bold=True)
                )
                typer.echo("I don't know how to solve this problem, exiting\n")
                return

            typer.echo(
                typer.style("Proposed Solution:", fg=typer.colors.GREEN, bold=True)
            )
            typer.echo(f"{proposed_solution}\n")

            user_action = prompt_action()

            if user_action == Action.EXIT:
                typer.echo("Exiting Claix.\n")
                return

            elif user_action == Action.REVISE:
                typer.echo(typer.style("Revision Needed:", fg=typer.colors.YELLOW, bold=True))
                typer.echo("Please provide more details or alternative instructions to improve the proposed solution.")
                
                revision_instructions = typer.prompt("Enter your revised instructions: ")
                command_run_result = bot.get_revised_command(revision_instructions)

            elif user_action == Action.RUN:
                command_run_result = run_shell_command(proposed_solution)
                error_iterations += 1

        if command_run_result.returncode == 0:
            if command_run_result.stdout:
                typer.echo(typer.style("Output:", fg=typer.colors.BLUE, bold=True))
                typer.echo(f"{command_run_result.stdout}")
            else:
                typer.echo(typer.style("No output.", fg=typer.colors.BLUE, bold=True))


if __name__ == "__main__":
    app()
