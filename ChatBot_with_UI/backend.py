
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Annotated

from langchain_core.messages import BaseMessage
from langchain_core.runnables import RunnableConfig
from langgraph.graph import add_messages

from langchain_groq import ChatGroq
from langgraph.checkpoint.sqlite import SqliteSaver

from dotenv import load_dotenv
import sqlite3

load_dotenv()


# =====================================
# 1. Define State
# =====================================

class ChatState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# =====================================
# 2. Initialize LLM
# =====================================

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0.9,
    max_tokens=1024,
    streaming=True
)


# =====================================
# 3. Chat Node
# =====================================

def chat_node(state: ChatState, config: RunnableConfig):

    messages = state['messages']

    response = llm.invoke(
        messages,
        config=config
    )

    return {
        'messages': [response]
    }


# =====================================
# 4. SQLite Checkpointer
# =====================================

conn = sqlite3.connect(
    database="chatbot.db",
    check_same_thread=False
)

checkpointer = SqliteSaver(conn)


# =====================================
# 5. Build Graph
# =====================================

graph = StateGraph(ChatState)

graph.add_node("chat_node", chat_node)

graph.add_edge(START, "chat_node")
graph.add_edge("chat_node", END)

chatbot = graph.compile(checkpointer=checkpointer)


# =====================================
# 6. Test (Optional)
# =====================================

# if __name__ == "__main__":

#     from langchain_core.messages import HumanMessage

#     config = {
#         "configurable": {
#             "thread_id": "thread-1"
#         }
#     }

#     response = chatbot.invoke(
#         {
#             "messages": [
#                 HumanMessage(content="What is the capital of Spain?")
#             ]
#         },
#         config=config
#     )

#     print(response["messages"][-1].content)