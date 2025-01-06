
import os
import openai
from git import Repo, GitCommandError
import shlex
from dotenv import load_dotenv
load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')

class AIGitBot:
    def __init__(self, repo_path):
        self.repo = Repo(repo_path)
        if self.repo.bare:
            raise Exception("The specified directory is not a valid Git repository.")

    def translate_to_git_commands(self, user_input):
        """
        Use OpenAI's API to translate natural language input into Git commands.
        The function will return all necessary steps such as git add, git commit, git push, or any other necessary operations based on user input.
        """
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that converts natural language instructions into valid Git commands. You should return only the necessary commands, no explanations. Make sure to include steps like 'git add .', 'git commit -m', 'git push', 'git pull', 'git checkout', etc., depending on the user request."},
                    {"role": "user", "content": f"Translate the following task into Git commands: {user_input}"}
                ],
                max_tokens=150,
                temperature=0.5
            )

            git_commands = response['choices'][0]['message']['content'].strip()
            
            commands = git_commands.split('\n')
            return [command.strip() for command in commands if command.strip()]

        except Exception as e:
            return [f"Error: {e}"]


    def execute_git_command(self, git_command):
        """
        Execute a Git command on the repository.
        """
        try:
            parsed_command = shlex.split(git_command)
            output = self.repo.git.execute(parsed_command)
            return f"Command executed successfully:\n{output}"
        except GitCommandError as e:
            return f"Git error: {e}"
        except Exception as e:
            return f"Error executing command: {e}"

    def handle_task(self, user_input):
        """
        Handle a task from the user and return the necessary Git commands.
        """
        commands = self.translate_to_git_commands(user_input)

        if not commands:
            return [{"error": "No commands generated."}]

        steps = [{"command": command, "type": "execute"} for command in commands]
        return steps

