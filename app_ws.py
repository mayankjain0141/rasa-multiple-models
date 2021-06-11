import os
import logging
import uuid
import socketio
from aiohttp import web
from rasa.core.agent import Agent
import sys



logging.basicConfig(
    level=logging.WARN,
    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
    datefmt='%m-%d %H:%M')

def __create_agent(lang):
    model_path = './models/model-{}.tar.gz'.format(lang)
    return Agent.load(model_path=model_path)
    
agents = {
    "en": __create_agent("en"),
    "es": __create_agent("es")
}

# Web app + routing
app = web.Application()

# Websocket through SocketIO with support for regular HTTP endpoints
sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
sio.attach(app)

@sio.on('session_request')
async def on_session_request(sid, data):    
    if data is None:
        data = {}
    if 'session_id' not in data or data['session_id'] is None:
        data['session_id'] = uuid.uuid4().hex
    await sio.emit('session_confirm', data['session_id'])

@sio.on('user_uttered')
async def on_user_uttered(sid, message):
    metadata = message.get('metadata', {})
    lang = metadata.get('lang', 'en')
    agent = agents.get(lang, 'Language {} is not supported'.format(lang))
    bot_response = await agent.handle_text(text_message=message.get('message'), sender_id=sid)
    await sio.emit('bot_uttered', bot_response, room=sid)

if __name__ == '__main__':
    
    modulename = 'Agent'
    if Agent not in sys.modules:
        print("hello")
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 5000))
    web.run_app(app, host=host, port=port)
