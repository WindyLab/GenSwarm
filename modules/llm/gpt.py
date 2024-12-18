"""
Copyright (c) 2024 WindyLab of Westlake University, China
All rights reserved.

This software is provided "as is" without warranty of any kind, either
express or implied, including but not limited to the warranties of
merchantability, fitness for a particular purpose, or non-infringement.
In no event shall the authors or copyright holders be liable for any
claim, damages, or other liability, whether in an action of contract,
tort, or otherwise, arising from, out of, or in connection with the
software or the use or other dealings in the software.
"""

import asyncio

from openai import AsyncOpenAI
from modules.llm import BaseLLM, model_manager
from tenacity import (
    retry,
    stop_after_attempt,
    wait_random_exponential,
    stop_after_delay,
)


class GPT(BaseLLM):
    """
        A class to interact with OpenAI's GPT model.

        This class handles requests to OpenAI's GPT models using an asynchronous client,
        providing retry mechanisms and optional streaming support.
    2024-11-04 09:38:28:051106]:Run code success</span>

        Args:
            memorize (bool): Whether to store previous interactions for context in future requests.
            stream_output (bool): Whether to receive partial outputs via streaming.
    """

    def __init__(
            self, memorize: bool = False, stream_output: bool = False, model: str = "GPT"
    ) -> None:
        """
        Initializes the GPT class by allocating a model, obtaining the necessary API
        credentials, and initializing the asynchronous client.

        Args:
            memorize (bool): Flag indicating if the class should store previous interactions.
            stream_output (bool): Flag indicating if output should be streamed.
        """
        self.api_base, self.key, self.model = model_manager.allocate(model_family=model)
        super().__init__(self.model, memorize, stream_output)
        self._client = AsyncOpenAI(api_key=self.key, base_url=self.api_base)

    @retry(
        stop=(stop_after_attempt(5) | stop_after_delay(500)),
        wait=wait_random_exponential(multiplier=1, max=60),
        reraise=True,
    )
    async def _make_request(self, temperature: float) -> str:
        """
        Sends a request to the GPT model and retrieves the result, with optional retry logic.

        This function handles both standard and streaming outputs. In streaming mode, it
        collects all the chunks and assembles them into a complete response.

        Args:
            temperature (float): Controls the randomness of the output. Higher values produce more varied responses.

        Returns:
            str: The final content returned by the GPT model.

        Raises:
            Exception: If an error occurs during the API call, it will be logged and re-raised.
        """
        try:
            response = await self._client.chat.completions.create(
                model=self._model,
                messages=self._memories,
                temperature=temperature,
                stream=self._stream_output,
            )

            if self._stream_output:
                # Handle streaming output
                collected_chunks = []
                collected_messages = []
                async for chunk in response:
                    collected_chunks.append(chunk)
                    choices = chunk.choices if hasattr(chunk, "choices") else []
                    if len(choices) > 0:
                        chunk_message = (
                            choices[0].delta if hasattr(choices[0], "delta") else {}
                        )
                        collected_messages.append(chunk_message)

                # Assemble full content from streaming chunks
                full_reply_content = "".join(
                    [
                        m.content
                        if hasattr(m, "content") and m.content is not None
                        else ""
                        for m in collected_messages
                    ]
                )
                return full_reply_content
            else:
                # Return the first message's content if not streaming
                return response.choices[0].message.content
        except Exception as e:
            from modules.file.log_file import logger

            logger.log(f"Error in _make_request: {e}", level="error")
            raise  # Re-raise the exception to trigger the retry logic

    async def _retry_request_with_sleep(self, temperature: float) -> str:
        """
        Continuously retries the GPT request with a delay between attempts.

        This method sleeps for 5 minutes between retries and continues until a successful
        request is made. It logs each retry attempt.

        Args:
            temperature (float): The temperature parameter to control the response randomness.

        Returns:
            str: The final result returned by the GPT model after a successful request.
        """
        from modules.file.log_file import logger

        while True:
            logger.log(
                "Sleeping for 5 minutes before retrying request...", level="info"
            )
            await asyncio.sleep(5 * 60)  # Sleep for 5 minutes

            try:
                # Attempt to make the request again after sleep
                result = await self._make_request(temperature)
                return result  # Return result upon success
            except Exception as e:
                logger.log(f"Request failed in sleep mode: {e}", level="error")
                continue  # Continue to retry if the request fails

    async def _ask_with_retry(self, temperature: float) -> str:
        """
        A helper method to perform the GPT model request with retry logic.

        If the maximum retry attempts (5) are exceeded, this method falls back to the
        retry-with-sleep strategy, where the request is retried every 5 minutes.

        Args:
            temperature (float): The temperature parameter for controlling the response variability.

        Returns:
            str: The final content returned by the GPT model, after handling retries or sleep mode.
        """
        from modules.file.log_file import logger

        try:
            # First attempt to make the request
            return await self._make_request(temperature)
        except Exception as re:
            logger.log(f"Exceeded 5 retries, entering sleep mode: {re}", level="error")
            # After retries are exhausted, switch to retry-with-sleep mode
            return await self._retry_request_with_sleep(temperature)


if __name__ == "__main__":
    gpt = GPT()
    response = asyncio.run(gpt.ask("Hello, who are you?"))
    print(response)
