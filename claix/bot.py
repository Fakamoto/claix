from openai import OpenAI
import time


class Bot:
    def __init__(self, assistant_id: str, thread_id: str = None):
        self.assistant_id = assistant_id
        self.thread_id = thread_id
        self.client = OpenAI()

    def __call__(self, prompt, thread_id = None):
        if not thread_id:
            thread_id = self.thread_id
            
        self.create_thread_message(prompt, thread_id)

        run = self.run_thread(thread_id)

        run = self.wait_for_run(run)

        return self.get_last_message(thread_id)

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

        updated_assistant = self.client.beta.assistants.update(
            self.assistant_id,
            file_ids=file_ids,
        )
