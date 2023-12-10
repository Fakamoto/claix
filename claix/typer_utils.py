import typer

from claix import __version__


# Version callback
def version_callback(show_version: bool):
    if show_version:
        typer.echo(__version__)
        raise typer.Exit()


# OpenAI API key callback
def openai_api_key_callback(api_key: str):
    if api_key is None:
        typer.echo(typer.style("Error:", fg=typer.colors.RED, bold=True))
        typer.echo("OPENAI_API_KEY environment variable is necessary to use Claix.")
        raise typer.Exit()
    return api_key


# Instructions callback
def instructions_callback(instructions: list[str]) -> str:
    if not instructions:
        typer.echo(typer.style("Error:", fg=typer.colors.RED, bold=True))
        typer.echo(
            "No instructions provided. Claix needs a set of instructions to generate commands.\n"
        )
        typer.echo(typer.style("Example Usage:", fg=typer.colors.BLUE, bold=True))
        typer.echo(
            "claix list all docker containers\nclaix show me active network interfaces"
        )
        raise typer.Exit()
    return instructions
