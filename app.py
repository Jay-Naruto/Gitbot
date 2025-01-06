from flask import Flask, render_template, request, jsonify
from gitbot import AIGitBot

app = Flask(__name__)
git_bot_instance = None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/setup", methods=["POST"])
def setup():
    try:
        global git_bot_instance
        repo_path = request.form.get("repo_path")
        git_bot_instance = AIGitBot(repo_path)
        return jsonify({"message": f"Git repository at '{repo_path}' initialized successfully."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/execute", methods=["POST"])
def execute():
    try:
        global git_bot_instance
        if git_bot_instance is None:
            return jsonify({"error": "Git repository is not set up. Please set up the repo first."}), 400

        user_input = request.form.get("command")
        steps = git_bot_instance.handle_task(user_input)  # Get all necessary git commands
        
        # Ensure steps are returned in the expected format
        if isinstance(steps, list):
            return jsonify({"commands": steps}), 200
        else:
            return jsonify({"error": "No valid commands generated."}), 400

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/execute_step", methods=["POST"])
def execute_step():
    try:
        global git_bot_instance
        if git_bot_instance is None:
            return jsonify({"error": "Git repository is not set up. Please set up the repo first."}), 400

        step_command = request.form.get("step_command")
        step_type = request.form.get("step_type")
        commit_message = request.form.get("commit_message") 

        if step_type == "commit":
            git_command = f"git commit -m '{commit_message}'"
        else:
            git_command = step_command

        output = git_bot_instance.execute_git_command(git_command)

        return jsonify({"output": output}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400


if __name__ == "__main__":
    app.run(debug=True)
