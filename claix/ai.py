import time
from typing import Optional
import instructor
from pydantic import BaseModel
from openai import OpenAI


class ClaixCommand(BaseModel):
    """
    A model describing important attributes of a CLI command.

    Attributes:
        is_command (bool): True if the response is a command, False otherwise 
            (e.g., if the output is a dot or is empty).
        command (Optional[str]): The string command to execute.
        explanation (Optional[str]): The explanation of the command.
    """
    is_command: bool
    command: Optional[str]
    explanation: Optional[str]


class Claix:
    def __init__(self, assistant_id: str, thread_id: str = None):
        self.assistant_id = assistant_id
        self.thread_id = thread_id
        self.client = OpenAI()

    def __call__(self, prompt, thread_id=None):
        if not thread_id:
            thread_id = self.thread_id

        self.create_thread_message(prompt, thread_id)

        run = self.run_thread(thread_id)

        run = self.wait_for_run(run)

        text_response: str = self.get_last_message(thread_id)

        claix_command: ClaixCommand = self.populate_model_from_text(ClaixCommand, text_response)

        if not claix_command.command:
            claix_command.is_command = False

        return claix_command

    def get_fixed_command(
        self, instructions: str, proposed_command: str, command_run_result
    ) -> ClaixCommand:
        error_prompt = (
            f"I want to: '{instructions}'\n"
            f"I tried '{proposed_command}'\n"
            f"but got this error: '{command_run_result.stderr}'\n\n"
            f"Having this error in mind, fix my original command of '{proposed_command}' "
            f"or give me a new command to solve: '{instructions}'"
        )

        command: ClaixCommand = self(error_prompt)

        return command

    def get_revised_command(
        self,
        revision_instructions: str,
        original_instructions: str,
        proposed_command: str,
    ) -> str:
        revision_prompt = (
            f"I want to: {original_instructions}\n"
            f"The proposed solution was: {proposed_command}\n\n"
            f"but I want to modify this solution considering this: {revision_instructions}\n\n"
            f"please give me a new solution considering that"
        )

        revised_solution: str = self(revision_prompt)

        return revised_solution

    @staticmethod
    def create_assistant(
        name: str,
        instructions: str,
        model: str = "gpt-4-1106-preview",
        tools: list[dict] = [{"type": "code_interpreter"}, {"type": "retrieval"}],
    ):
        client = OpenAI()
        assistant = client.beta.assistants.create(
            name=name,
            instructions=instructions,
            tools=tools,
            model=model,
        )
        return assistant

    @staticmethod
    def create_thread():
        client = OpenAI()
        thread = client.beta.threads.create()
        return thread

    @staticmethod
    def populate_model_from_text(model: BaseModel, text: str) -> BaseModel:
        client = instructor.patch(OpenAI())
        """Populates a pydantic model from a text."""
        response: model = client.chat.completions.create(
            model="gpt-3.5-turbo",
            response_model=model,
            messages=[
                {"role": "user", "content": text},
            ],
            max_retries=3,
        )
        return response

    def create_thread_message(self, prompt: str, thread_id: str):
        message = self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=prompt,
        )
        return message

    def run_thread(self, thread_id: str):
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=self.assistant_id,
        )
        return run

    def update_run(self, run):
        run = self.client.beta.threads.runs.retrieve(
            run_id=run.id,
            thread_id=run.thread_id,
        )
        return run

    def wait_for_run(self, run):
        while run.status != "completed":
            run = self.update_run(run)
            time.sleep(0.1)
        return run

    def get_thread_messages(self, thread_id: str):
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id,
        )
        return messages

    def get_last_message(self, thread_id: str):
        messages = self.get_thread_messages(thread_id)
        return list(messages)[0].content[0].text.value

    def add_files_to_assistant(self, file_ids: str | list[str]):
        if isinstance(file_ids, str):
            file_ids = [file_ids]

        self.client.beta.assistants.update(
            self.assistant_id,
            file_ids=file_ids,
        )
