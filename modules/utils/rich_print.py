from rich.panel import Panel
from rich import print
from rich.syntax import Syntax
from rich.prompt import Prompt


def rich_print(title, content, subtitle=""):
    panel = Panel(
        content,
        title=f"[bold cyan]{title}[/bold cyan]",
        border_style="cyan",  # Border color
        subtitle=f"[bold cyan]{subtitle}[/bold cyan]",
    )
    print(panel)


def rich_code_print(title, code, subtitle=""):
    if subtitle:
        subtitle = f"[bold cyan]{subtitle}.py[/bold cyan]"
    syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
    panel = Panel(
        syntax,
        title=f"[bold cyan]{title}[/bold cyan]",
        border_style="cyan",
        subtitle=subtitle,
    )
    print(panel)

def rich_input(prompt_text, default_value="", subtitle=""):
    """ Mimics input() with rich styling """
    prompt = f"[bold cyan]{prompt_text}[/bold cyan]: "
    user_input = Prompt.ask(prompt, default=default_value)
    # if subtitle:
    #     subtitle = f"[bold cyan]{subtitle}[/bold cyan]"
    # panel = Panel(
    #     user_input,
    #     title=f"[bold cyan]{prompt_text}[/bold cyan]",
    #     border_style="cyan",
    #     subtitle=subtitle,
    # )
    # print(panel)
    return user_input