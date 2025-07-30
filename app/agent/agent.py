"""
Main agent orchestrator that connects the LLM with tools and manages the conversation flow.
"""
from typing import List, Dict, Any, Optional
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.agents import AgentAction, AgentFinish
from langchain_openai import ChatOpenAI  # This is a placeholder, we'll use Groq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool

from app.agent.llm import get_llm
from app.agent.tools.binance_tool import BinancePriceTool
from app.agent.tools.kb_tool import KnowledgeBaseTool
from app.agent.tools.rejection_tool import RejectionTool
from app.agent.prompts import SYSTEM_PROMPT
from app.config import settings

class CryptoAgent:
    """
    Crypto AI Agent that orchestrates the tools, LLM, and conversation flow.
    """
    
    def __init__(self):
        """Initialize the Crypto Agent with LLM and tools."""
        self.llm = get_llm()
        self.tools = self._initialize_tools()
        self.agent_executor = self._create_agent_executor()
        self.memory = []  # Simple list to store conversation history

        
    def _initialize_tools(self) -> List[BaseTool]:
        """Initialize and return the tools used by the agent."""
        tools = []
        
        try:
            binance_tool = BinancePriceTool()
            tools.append(binance_tool)
            print(f"✅ Successfully initialized: {binance_tool.name}")
        except Exception as e:
            print(f"❌ Failed to initialize BinancePriceTool: {e}")
        
        try:
            kb_tool = KnowledgeBaseTool()
            tools.append(kb_tool)
            print(f"✅ Successfully initialized: {kb_tool.name}")
        except Exception as e:
            print(f"❌ Failed to initialize KnowledgeBaseTool: {e}")
        
        try:
            rejection_tool = RejectionTool()
            tools.append(rejection_tool)
            print(f"✅ Successfully initialized: {rejection_tool.name}")
        except Exception as e:
            print(f"❌ Failed to initialize RejectionTool: {e}")
        
        print(f"📋 Total tools initialized: {len(tools)}")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description[:100]}...")
        
        return tools
        
    
    def _create_agent_executor(self) -> AgentExecutor:
        """Create and return the LangChain agent executor."""
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create agent with tools using the newer LangChain approach
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True,
            return_intermediate_steps=True
        )
    
    def _update_memory(self, user_input: str, assistant_response: str):
        """
        Update the conversation memory with the latest exchange.
        
        Args:
            user_input: The user's message
            assistant_response: The agent's response
        """
        # Add the latest exchange to memory
        self.memory.append({"role": "human", "content": user_input})
        self.memory.append({"role": "assistant", "content": assistant_response})
        
        # Trim memory to configured window size
        if len(self.memory) > settings.MEMORY_WINDOW * 2:  # *2 because each exchange has 2 messages
            self.memory = self.memory[-settings.MEMORY_WINDOW * 2:]
    
    def _format_chat_history(self) -> List[Dict[str, str]]:
        """Format the memory into chat history messages for the agent."""
        chat_history = []
        
        for msg in self.memory:
            if msg["role"] == "human":
                chat_history.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                chat_history.append(AIMessage(content=msg["content"]))
        
        return chat_history
    
    async def process_message(self, user_input: str) -> str:
        """
        Process a user message and return the agent's response.
        
        Args:
            user_input: The user's message
            
        Returns:
            The agent's response
        """
        chat_history = self._format_chat_history()
        
        # Execute the agent with the user input and chat history
        response = await self.agent_executor.ainvoke({
            "input": user_input,
            "chat_history": chat_history
        })
        
        # Get the final output
        output = response["output"]
        
        # Update memory with this exchange
        self._update_memory(user_input, output)
        
        return output