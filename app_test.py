import os
import logging
import uuid
import asyncio
from flask import Flask
from flask_cors import CORS, cross_origin
from flask import request
from rasa.core.agent import Agent

app = Flask(__name__)
CORS(app)
cors = CORS(app, resources={r"/*": {"origins": "*"}})

action_endpoint = "http://localhost:5055/webhook"


def agent_get(lang):
    agents = {"en": './models/model-en.tar.gz',
              "es": './models/model-es.tar.gz'}


    ok = Agent.load(model_path= agents[lang],
                    model_server = "http://192.168.1.34:5000/")
    return ok


async def process(agent, msg):
    output = await agent.handle_text(msg)
    print(output)
    return output


@app.route('/message')
@cross_origin(origin='*')
def new_message():
    if not request.json:
        abort(400)
    orgId = request.args.get('lang')
    current_agent = agent_get(lang)
    user = request.json['sender']
    message = request.json['message']
    res = (current_agent.handle_text(text_message=message, sender_id=user))
    message = asyncio.run(process(current_agent, message))
    message = json.dumps(message)
    return message

# @app.route('/')
# def user_uttered():
#     sid = str(request.args.get('sid'))
#     message = str(request.args.get('message'))
#     lang = str(request.args.get('lang', 'en'))
#     agent = agents.get(lang, 'Language {} is not supported'.format(lang))
#     bot_response = loop.run_until_complete(
#         agent.handle_text(text_message=message, sender_id=sid)
#     )
#     return ', '.join(map(str, bot_response))



if __name__ == '__main__':
    app.run(host='localhost', port=5000, debug=False, use_reloader=False)