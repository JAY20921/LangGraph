import streamlit as st
from backend import chatbot
from langchain_core.messages import HumanMessage
import asyncio

async def stream_generator():
    async for chunk, metadata in chatbot.astream(
        {'messages': [HumanMessage(content='Write 5 words')]}, 
        config={'configurable': {'thread_id': 'test'}}, 
        stream_mode='messages'
    ):
        yield chunk.content

st.write("Starting stream...")
st.write_stream(stream_generator())
