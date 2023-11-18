# src/main.py
import typer

app = typer.Typer()

@app.command()
def main():
    print("Hello")

if __name__ == "__main__":
    app()
