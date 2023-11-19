# src/main.py
from claix.bot import Bot
from claix.utils import get_or_create_default_assistant_id, get_or_create_default_thread_id, run_shell_command, simulate_clear
from rich.panel import Panel
from rich.text import Text
from rich.console import Console
import rich
import typer

app = typer.Typer(name="claix", no_args_is_help=True, add_completion=False)
console = Console()
        
@app.command(help="Turns your instructions into CLI commands ready to execute.")
def main(instructions: list[str] = typer.Argument(None, help="The instructions that you want to execute. Pass them as a list of strings.", )):
    """
    Claix is a command line assistant that helps you translate instructions into CLI commands.

    Example: claix list all docker containers

    You can give it a set of instructions, and it will attempt to generate
    the appropriate command-line commands to execute.

    Args:
    instructions: Your instructions as text.
    """
    simulate_clear(console)
    if not instructions:
        # If no instructions are provided, display a helpful message and an example usage
        error_message = Text("No instructions provided. Claix needs a set of instructions to generate commands.", style="white")
        example_usage = Text("Example usage:\nclaix list all docker containers\nclaix show me active network interfaces", style="white")
        rich.print(Panel(error_message, title="[bold]Error[/bold]", expand=False, border_style="red"))
        rich.print(Panel(example_usage, title="[bold]Example Usage[/bold]", expand=False, border_style="green"))
        return
    instructions: str = " ".join(instructions)
    rich.print(Panel(Text(instructions, style="white"), title="Instructions\U0001F4DD", expand=False, border_style="blue"))
    assistant_id = get_or_create_default_assistant_id()
    thread_id = get_or_create_default_thread_id()

    bot = Bot(assistant_id, thread_id)
    
    rich.print(Panel(Text("Thinking...", style="white"), title="Claix", expand=False, border_style="purple"))
    proposed_command: str = bot(instructions)
    if proposed_command == ".":
        rich.print(Panel(Text("I don't know how to solve this problem, exiting", style="white"), title="Claix", expand=False, border_style="purple"))
        return
    rich.print(Panel(proposed_command, title="Command\U0001F4BB", expand=False, border_style="green", padding=(1, 2)))

    # Ask if user wants Claix to run the command
    prompt_text = Text("Run command? Press Enter to run or [Y/n]", style="white", end="")
    rich.print(Panel(prompt_text, title="Action\u2757", expand=False, border_style="yellow"), end="")
    run_command_input = input()
    run_command = run_command_input.lower() in ["y", "yes", ""]
    simulate_clear(console)

    if not run_command:
        return
    
    result = run_shell_command(proposed_command)

    error_iterations = 0
    while result.returncode != 0:
        if error_iterations > 2:
            simulate_clear(console)
            rich.print(Panel(Text("Too many errors, exiting", style="white"), title="Error", expand=False, border_style="red"))
            break

        rich.print(Panel(Text(instructions, style="white"), title="Instructions\U0001F4DD", expand=False, border_style="blue"))
        rich.print(Panel(Text(f"Error iteration {error_iterations}", style="white"), title="Error iteration", expand=False, border_style="red"))
        rich.print(Panel(result.stderr, title="Error", expand=False, border_style="red"))
        error_prompt = \
f"""I want to: '{instructions}'
I tried '{proposed_command}'
but got this error: '{result.stderr}'

Having this error in mind, fix my original command of '{proposed_command}' or give me a new command to solve: '{instructions}'"""
        
        
        rich.print(Panel(Text("Thinking...", style="white"), title="Claix", expand=False, border_style="purple"))
        proposed_solution = bot(error_prompt)

        if proposed_solution == ".":
            rich.print(Panel(Text("I don't know how to solve this problem, exiting", style="white"), title="Claix", expand=False, border_style="purple"))
            return

        rich.print(Panel(proposed_solution, title="Command\U0001F4BB", expand=False, border_style="green", padding=(1, 2)))
        # Ask if user wants Claix to run the command
        prompt_text = Text("Run command? Press Enter to run or [Y/n]", style="white", end="")
        rich.print(Panel(prompt_text, title="Action\u2757", expand=False, border_style="yellow"), end="")
        run_command_input = input()
        run_command = run_command_input.lower() in ["y", "yes", ""]
        simulate_clear(console)

        if not run_command:
            return
        
        result = run_shell_command(proposed_solution)
        error_iterations += 1

    else:
        simulate_clear(console)
        # success
        if result.stdout:
            rich.print(Panel(result.stdout, title="Output", expand=False, border_style="blue"))



if __name__ == "__main__":
    app()