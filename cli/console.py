from rich.console import Console

console = Console()


class CustomPrint:
    @staticmethod
    def print(msg, *args, **kwargs):
        console.print(msg, *args, **kwargs)

    @staticmethod
    def success(msg: str):
        console.print(f"[bold green]Success:[/bold green] {msg}")

    @staticmethod
    def info(msg: str):
        console.print(f"[bold blue]Info:[/bold blue] {msg}")

    @staticmethod
    def warning(msg: str):
        console.print(f"[bold yellow]Warning:[/bold yellow] {msg}")

    @staticmethod
    def error(msg: str):
        console.print(f"[bold red]Error:[/bold red] {msg}")

    @staticmethod
    def debug(msg: str):
        console.print(f"[bold magenta]Debug:[/bold magenta] {msg}")
