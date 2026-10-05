
import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
load_dotenv()
import uuid

if 'thread_id' not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

config = {'configurable': {'thread_id': st.session_state.thread_id}}

if 'message_history' not in st.session_state:
    st.session_state.message_history = []

message_history = st.session_state.message_history

for message in message_history:
    with st.chat_message(message['role']):
        st.markdown(message['content'])
user_input = st.chat_input('Say something :',key='user_input')

if user_input:
    st.session_state.message_history.append({'role': 'user', 'content': user_input})
    with st.chat_message('user'):
        st.write(user_input)
    with st.chat_message('ai'):
        async def stream_generator():
            async for message_chunk, metadata in chatbot.astream(
                 {'messages': [HumanMessage(content=user_input)]}, config=config, stream_mode='messages'
            ):
                yield message_chunk.content
                
        ai_message = st.write_stream(stream_generator())
    st.session_state.message_history.append({'role': 'ai', 'content': ai_message})
