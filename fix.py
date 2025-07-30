#!/usr/bin/env python
"""
Script to fix compatibility issues with LangChain and Pydantic v2.
This script modifies the agent.py file to use the newer LangChain agent creation approach
and installs the necessary compatibility packages.
"""
import os
import subprocess
import sys

def update_agent_file():
    """Update the agent.py file to be compatible with the latest LangChain version."""
    agent_file_path = "app/agent/agent.py"
    
    # Check if the file exists
    if not os.path.exists(agent_file_path):
        print(f"Error: {agent_file_path} not found")
        return
    
    # Read the current content
    with open(agent_file_path, "r") as f:
        content = f.read()
    
    # Replace the import for create_openai_tools_agent
    new_content = content.replace(
        "from langchain.agents import AgentExecutor, create_openai_tools_agent",
        "from langchain.agents import AgentExecutor\nfrom langchain_core.agents import AgentAction, AgentFinish\nfrom langchain.prompts import ChatPromptTemplate, MessagesPlaceholder"
    )
    
    # Replace the _create_agent_executor method
    old_method = """    def _create_agent_executor(self) -> AgentExecutor:
        \"\"\"Create and return the LangChain agent executor.\"\"\"
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )"""
    
    new_method = """    def _create_agent_executor(self) -> AgentExecutor:
        \"\"\"Create and return the LangChain agent executor.\"\"\"
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create agent with tools (compatible with newer LangChain)
        return AgentExecutor.from_llm_and_tools(
            llm=self.llm,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )"""
    
    new_content = new_content.replace(old_method, new_method)
    
    # Write the updated content
    with open(agent_file_path, "w") as f:
        f.write(new_content)
    
    print(f"Updated {agent_file_path} for better compatibility")

def update_requirements():
    """Update requirements.txt with more specific versions for compatibility."""
    requirements_file = "requirements.txt"
    
    # Check if the file exists
    if not os.path.exists(requirements_file):
        print(f"Error: {requirements_file} not found")
        return
    
    # Updated requirements with specific versions
    updated_requirements = """# API Framework
fastapi>=0.103.1
uvicorn>=0.23.2
pydantic>=2.4.2
pydantic-settings>=2.0.3
pydantic-core>=2.10.1

# Pydantic v1 compatibility
typing-extensions>=4.7.1
pydantic-extra-types>=2.0.0

# LLM and Agent
langchain>=0.0.267
langchain-community>=0.0.10
langchain-core>=0.0.27
langchain-groq>=0.0.1

# Vector Database
chromadb>=0.4.18
qdrant-client>=1.6.0
# pinecone-client>=2.2.2  # Uncomment if using Pinecone

# Embedding Models
sentence-transformers>=2.2.2
transformers>=4.34.0
torch>=2.0.0

# Document Processing
unstructured>=0.10.0
pdf2image>=1.16.3
pytesseract>=0.3.10
python-docx>=0.8.11
pypdf>=3.16.0

# Utilities
python-dotenv>=1.0.0
requests>=2.31.0
pandas>=2.0.0
numpy>=1.24.0
tqdm>=4.66.1

# Testing
pytest>=7.4.2
pytest-asyncio>=0.21.1
"""
    
    # Write the updated requirements
    with open(requirements_file, "w") as f:
        f.write(updated_requirements)
    
    print(f"Updated {requirements_file} with compatible package versions")

def install_pydantic_v1_compatibility():
    """Install pydantic-v1 compatibility package."""
    print("Installing pydantic v1 compatibility package...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pydantic[v1]"])
        print("Successfully installed pydantic v1 compatibility")
    except subprocess.CalledProcessError as e:
        print(f"Error installing pydantic v1 compatibility: {e}")
        print("Please run manually: pip install pydantic[v1]")

def main():
    """Run all compatibility fixes."""
    install_pydantic_v1_compatibility()
    update_agent_file()
    update_requirements()
    print("Compatibility fixes applied. Please run 'pip install -r requirements.txt' to update dependencies.")

if __name__ == "__main__":
    main()
#!/usr/bin/env python
"""
Script to fix compatibility issues with LangChain and Pydantic v2.
This script modifies the agent.py file to use the newer LangChain agent creation approach.
"""
import os

def update_agent_file():
    """Update the agent.py file to be compatible with the latest LangChain version."""
    agent_file_path = "app/agent/agent.py"
    
    # Check if the file exists
    if not os.path.exists(agent_file_path):
        print(f"Error: {agent_file_path} not found")
        return
    
    # Read the current content
    with open(agent_file_path, "r") as f:
        content = f.read()
    
    # Replace the import for create_openai_tools_agent
    new_content = content.replace(
        "from langchain.agents import AgentExecutor, create_openai_tools_agent",
        "from langchain.agents import AgentExecutor\nfrom langchain_core.agents import AgentAction, AgentFinish\nfrom langchain_openai import ChatOpenAI  # This is a placeholder, we'll use Groq"
    )
    
    # Replace the _create_agent_executor method
    old_method = """    def _create_agent_executor(self) -> AgentExecutor:
        \"\"\"Create and return the LangChain agent executor.\"\"\"
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        agent = create_openai_tools_agent(self.llm, self.tools, prompt)
        
        return AgentExecutor(
            agent=agent,
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )"""
    
    new_method = """    def _create_agent_executor(self) -> AgentExecutor:
        \"\"\"Create and return the LangChain agent executor.\"\"\"
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad")
        ])
        
        # Create agent with tools (LangChain 0.1.0+ compatible)
        # In newer LangChain, we use the tool-calling capability of the LLM directly
        return AgentExecutor(
            agent=self.llm.bind_tools(self.tools),
            tools=self.tools,
            verbose=True,
            handle_parsing_errors=True
        )"""
    
    new_content = new_content.replace(old_method, new_method)
    
    # Write the updated content
    with open(agent_file_path, "w") as f:
        f.write(new_content)
    
    print(f"Updated {agent_file_path} for better compatibility")

def update_requirements():
    """Update requirements.txt with more specific versions for compatibility."""
    requirements_file = "requirements.txt"
    
    # Check if the file exists
    if not os.path.exists(requirements_file):
        print(f"Error: {requirements_file} not found")
        return
    
    # Updated requirements with specific versions
    updated_requirements = """# API Framework
fastapi==0.103.1
uvicorn==0.23.2
pydantic==2.4.2
pydantic-settings==2.0.3

# LLM and Agent
langchain==0.1.0
langchain-community==0.0.11
langchain-core==0.1.1
langchain-groq==0.0.1
langchain-openai==0.0.2

# Vector Database
chromadb==0.4.18
qdrant-client==1.6.0
# pinecone-client==2.2.2  # Uncomment if using Pinecone

# Embedding Models
sentence-transformers==2.2.2
transformers==4.34.0
torch>=2.0.0

# Document Processing
unstructured>=0.10.0
pdf2image>=1.16.3
pytesseract>=0.3.10
python-docx>=0.8.11
pypdf>=3.16.0

# Utilities
python-dotenv>=1.0.0
requests>=2.31.0
pandas>=2.0.0
numpy>=1.24.0
tqdm>=4.66.1

# Testing
pytest>=7.4.2
pytest-asyncio>=0.21.1
"""
    
    # Write the updated requirements
    with open(requirements_file, "w") as f:
        f.write(updated_requirements)
    
    print(f"Updated {requirements_file} with compatible package versions")

def main():
    """Run all compatibility fixes."""
    update_agent_file()
    update_requirements()
    print("Compatibility fixes applied. Please run 'pip install -r requirements.txt' to update dependencies.")

if __name__ == "__main__":
    main()