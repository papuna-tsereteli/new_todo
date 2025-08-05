import os
from typing import List, TypedDict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field  # Updated import
from langgraph.graph import StateGraph, END

# --- Get Google API Key ---
# Make sure to set your GOOGLE_API_KEY in your .env file
from dotenv import load_dotenv

load_dotenv()


# The langchain library will automatically use the GOOGLE_API_KEY environment variable

# --- Output Schema Definition ---
# Define the structure of the AI's response
class SuggestedTasks(BaseModel):
    """A list of suggested to-do items."""
    tasks: List[str] = Field(description="A list of 3 to 5 relevant to-do item suggestions.")


# --- Graph State Definition ---
# Define the state that will be passed between nodes in the graph
class GraphState(TypedDict):
    existing_tasks: List[str]
    suggestions: List[str]


# --- LangGraph Node ---
def suggestion_node(state: GraphState):
    """
    Generates task suggestions based on the existing tasks.
    """
    print("---GENERATING SUGGESTIONS WITH GEMINI---")
    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are an expert to-do list assistant. Your goal is to help users build out their task lists by suggesting relevant next steps. "
                "Analyze the user's existing tasks and provide a list of 3 to 5 new, relevant to-do items. "
                "For example, if the user has 'Plan vacation', you might suggest 'Book flights', 'Reserve hotel', and 'Create packing list'.",
            ),
            (
                "human",
                "Here are my current tasks, please suggest what I should add next:\n\n"
                "```\n{tasks}\n```"
            ),
        ]
    )

    # Initialize the Chat model
    # Using a current and recommended Gemini model
    llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash", convert_system_message_to_human=True)

    # Create a chain that binds the structured output schema to the model
    structured_llm = llm.with_structured_output(SuggestedTasks)

    # Format the existing tasks for the prompt
    task_list_str = "\n".join(f"- {task}" for task in state["existing_tasks"])

    # Create the chain to be executed
    chain = prompt | structured_llm

    # Invoke the chain with the user's tasks
    ai_response = chain.invoke({"tasks": task_list_str})

    return {"suggestions": ai_response.tasks}


# --- Graph Builder ---
def get_suggestions_graph():
    """
    Builds and compiles the LangGraph for generating suggestions.
    """
    workflow = StateGraph(GraphState)

    # Add the single node to the workflow
    workflow.add_node("suggest", suggestion_node)

    # Define the entry and end points of the graph
    workflow.set_entry_point("suggest")
    workflow.add_edge("suggest", END)

    # Compile the graph into a runnable object
    return workflow.compile()
