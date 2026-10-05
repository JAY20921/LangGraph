
import streamlit as st
import uuid

from backend import chatbot
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv
load_dotenv()


# ==========================================
# 1. Utility Functions
# ==========================================

def generate_thread_id():
    return str(uuid.uuid4())


# ==========================================
# 2. Initialize Session State
# ==========================================

if 'thread_id' not in st.session_state:
    st.session_state.thread_id = generate_thread_id()

if 'message_history' not in st.session_state:
    st.session_state.message_history = []

if 'chat_threads' not in st.session_state:
    st.session_state.chat_threads = [
        {
            'id': st.session_state.thread_id,
            'name': 'Chat 1'
        }
    ]


# ==========================================
# 3. Thread Management
# ==========================================

def add_thread(thread_id):
    existing_ids = [
        thread['id'] for thread in st.session_state.chat_threads
    ]

    if thread_id not in existing_ids:
        st.session_state.chat_threads.append({
            'id': thread_id,
            'name': f'Chat {len(st.session_state.chat_threads) + 1}'
        })


def reset_chat():
    new_thread_id = generate_thread_id()

    st.session_state.thread_id = new_thread_id
    st.session_state.message_history = []

    add_thread(new_thread_id)


def load_conversation(thread_id):
    st.session_state.thread_id = thread_id

    config = {
        'configurable': {
            'thread_id': thread_id
        }
    }

    try:
        state = chatbot.get_state(config)

        messages = state.values.get('messages', [])

        history = []

        for message in messages:
            if isinstance(message, HumanMessage):
                history.append({
                    'role': 'user',
                    'content': message.content
                })

            elif message.type == 'ai':
                history.append({
                    'role': 'ai',
                    'content': message.content
                })

        st.session_state.message_history = history

    except Exception:
        st.session_state.message_history = []


# ==========================================
# 4. LangGraph Configuration
# ==========================================

config = {
    'configurable': {
        'thread_id': st.session_state.thread_id
    }
}


# ==========================================
# 5. Streamlit Sidebar
# ==========================================

st.sidebar.title('LangGraph Chatbot')

if st.sidebar.button('➕ New Chat', use_container_width=True):
    reset_chat()
    st.rerun()

st.sidebar.divider()

st.sidebar.subheader('Chat History')

for thread in st.session_state.chat_threads:

    if st.sidebar.button(
        thread['name'],
        key=thread['id'],
        use_container_width=True
    ):
        load_conversation(thread['id'])
        st.rerun()

st.sidebar.divider()

st.sidebar.caption(
    f"Thread ID: {st.session_state.thread_id}"
)



st.title('🤖 My LangGraph Chatbot')

for message in st.session_state.message_history:

    with st.chat_message(message['role']):
        st.markdown(message['content'])


user_input = st.chat_input(
    'Say something...',
    key='user_input'
)

if user_input:

    # Display user message
    st.session_state.message_history.append({
        'role': 'user',
        'content': user_input
    })

    with st.chat_message('user'):
        st.markdown(user_input)

    with st.chat_message('ai'):

        async def stream_generator():

            async for message_chunk, metadata in chatbot.astream(
                {
                    'messages': [
                        HumanMessage(content=user_input)
                    ]
                },
                config=config,
                stream_mode='messages'
            ):

                if message_chunk.content:
                    yield message_chunk.content

        ai_message = st.write_stream(stream_generator())

    st.session_state.message_history.append({
        'role': 'ai',
        'content': ai_message
    })