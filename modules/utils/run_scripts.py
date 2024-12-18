import asyncio
import os
import sys


async def run_script(
    working_directory,
    command=[],
    print_output=False,
    timeout=30,
    env=None,
) -> str:
    from modules.file import logger

    working_directory = str(working_directory)
    env = os.environ.copy() if env is None else env

    process = await asyncio.create_subprocess_exec(
        *command,
        cwd=working_directory,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
        env=env,
    )

    stdout_chunks, stderr_chunks = [], []

    async def read_stream(stream, accumulate, is_stdout=True):
        while True:
            line_bytes = await stream.readline()
            if not line_bytes:
                break
            line = line_bytes.decode("utf-8")
            accumulate.append(line)
            if print_output:
                print(
                    line,
                    end="" if is_stdout else "",
                    file=sys.stderr if not is_stdout else None,
                )

    try:
        # Apply timeout to the gather call using asyncio.wait_for

        await asyncio.wait_for(
            asyncio.gather(
                read_stream(process.stdout, stdout_chunks, is_stdout=True),
                read_stream(process.stderr, stderr_chunks, is_stdout=False),
            ),
            timeout=timeout,
        )

        if (
            "WARNING: cannot load logging configuration file, logging is disabled\n"
            in stderr_chunks
        ):
            stderr_chunks.remove(
                "WARNING: cannot load logging configuration file, logging is disabled\n"
            )
        if stderr_chunks:
            return "\n".join(stderr_chunks)
        else:
            return "NONE"

    except asyncio.TimeoutError:
        logger.log(content="Timeout", level="error")
        process.kill()
        await process.wait()  # Ensure the process is terminated
        return "Timeout"
    except asyncio.CancelledError:
        logger.log(content="Cancelled", level="error")
        process.kill()
        await process.wait()  # Ensure the process is terminated
        raise
    except Exception as e:
        logger.log(content=f"error in run code: {e}", level="error")
        process.kill()
        await process.wait()  # Ensure the process is terminated
        return f"error in run code: {e}"
    finally:
        # Ensure the process is terminated in case of any other unexpected errors
        if process.returncode is None:  # Check if process is still running
            process.kill()
            await process.wait()
