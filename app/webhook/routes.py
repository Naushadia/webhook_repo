from flask import Blueprint, request, jsonify, render_template
from ..extensions import client

webhook = Blueprint("Webhook", __name__, url_prefix="/webhook")


@webhook.route("/receiver", methods=["POST"])
def receiver():
    collection = client.db["webhook_store"]
    data = request.get_json()

    extracted_data = {
        "request_id": None,
        "author": None,
        "action": None,
        "from_branch": None,
        "to_branch": None,
        "timestamp": None,
    }

    event = request.headers.get("X-GitHub-Event")

    if event == "push":
        extracted_data["request_id"] = data["head_commit"]["id"]
        extracted_data["author"] = data["head_commit"]["author"]["name"]
        extracted_data["action"] = "push"
        extracted_data["from_branch"] = data["ref"].split("/")[-1]
        extracted_data["timestamp"] = data["head_commit"]["timestamp"]

    elif event == "pull_request":
        action = data["action"]
        extracted_data["request_id"] = data["pull_request"]["id"]
        extracted_data["author"] = data["pull_request"]["user"]["login"]
        extracted_data["action"] = action
        extracted_data["from_branch"] = data["pull_request"]["head"]["ref"]
        extracted_data["to_branch"] = data["pull_request"]["base"]["ref"]
        extracted_data["timestamp"] = data["pull_request"]["created_at"]

        if action == "closed" and data["pull_request"]["merged"]:
            extracted_data["action"] = "merge"
            extracted_data["timestamp"] = data["pull_request"]["merged_at"]

    collection.insert_one(extracted_data)
    return {}, 200


@webhook.route("/ui", methods=["GET"])
def ui():
    return render_template("webhook.html")


@webhook.route("/receiver", methods=["GET"])
def get_all_data():
    collection = client.db["webhook_store"]
    data = list(collection.find({}, {"_id": 0}))
    return jsonify(data), 200
