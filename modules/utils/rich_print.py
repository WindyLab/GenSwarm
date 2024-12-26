from rich.panel import Panel
from rich import print
from rich.syntax import Syntax
from rich.prompt import Prompt
from rich.live import Live
import time


def rich_print(
        title,
        content,
        subtitle="",
        streaming=True,  # 是否流式输出
        refresh_per_second=4,  # Live区域的刷新频率
        line_delay=0.3  # 每一行输出之间的等待时间
):
    """
    直接输出或流式输出一个带有标题、子标题、内容的面板。
    :param title: 标题
    :param content: 面板的文本内容
    :param subtitle: 子标题
    :param streaming: 是否以流式（逐行）方式输出
    :param refresh_per_second: 当 streaming=True 时, Live 的刷新频率
    :param line_delay: 当 streaming=True 时, 每一行输出之间等待时间(秒)
    """
    # 如果不需要流式输出，直接一次性打印面板即可
    if not streaming:
        panel = Panel(
            content,
            title=f"[bold cyan]{title}[/bold cyan]",
            border_style="cyan",
            subtitle=f"[bold cyan]{subtitle}[/bold cyan]",
        )
        print(panel)
        return

    # 需要流式输出时
    lines = content.split("\n")  # 拆分多行
    # 先构造一个空面板或者初始内容的面板
    panel = Panel(
        "",
        title=f"[bold cyan]{title}[/bold cyan]",
        border_style="cyan",
        subtitle=f"[bold cyan]{subtitle}[/bold cyan]",
    )
    with Live(panel, refresh_per_second=refresh_per_second) as live:
        for i in range(1, len(lines) + 1):
            # 把前 i 行拼到一起，作为当前输出内容
            current_content = "\n".join(lines[:i])
            # 更新面板
            panel = Panel(
                current_content,
                title=f"[bold cyan]{title}[/bold cyan]",
                border_style="cyan",
                subtitle=f"[bold cyan]{subtitle}[/bold cyan]",
            )
            live.update(panel)
            time.sleep(line_delay)  # 等待一下，让“流式”效果可见


def rich_code_print(
        title,
        code,
        subtitle="",
        streaming=True,  # 是否流式输出
        refresh_per_second=10,  # Live区域的刷新频率
        line_delay=0.1  # 逐行输出延迟
):
    """
    直接输出或流式输出一个带有标题、子标题、代码高亮的面板。
    :param title: 标题
    :param code: 代码字符串
    :param subtitle: 子标题
    :param streaming: 是否以流式（逐行）方式输出
    :param refresh_per_second: 当 streaming=True 时, Live 的刷新频率
    :param line_delay: 当 streaming=True 时, 每一行输出之间的等待时间(秒)
    """
    # 如果不需要流式输出，直接一次性打印面板即可
    if not streaming:
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
        return

    # 需要流式输出时，拆分代码为多行
    code_lines = code.split("\n")
    if subtitle:
        subtitle = f"[bold cyan]{subtitle}.py[/bold cyan]"

    # 初始化面板为空或初始内容
    syntax_initial = Syntax("", "python", theme="monokai", line_numbers=True)
    panel = Panel(
        syntax_initial,
        title=f"[bold cyan]{title}[/bold cyan]",
        border_style="cyan",
        subtitle=subtitle,
    )
    with Live(panel, refresh_per_second=refresh_per_second) as live:
        for i in range(1, len(code_lines) + 1):
            # 取前 i 行组合
            partial_code = "\n".join(code_lines[:i])
            syntax_new = Syntax(partial_code, "python", theme="monokai", line_numbers=True)
            panel = Panel(
                syntax_new,
                title=f"[bold cyan]{title}[/bold cyan]",
                border_style="cyan",
                subtitle=subtitle,
            )
            live.update(panel)
            time.sleep(line_delay)


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
