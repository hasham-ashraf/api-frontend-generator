from typing import List
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

class ArchitectureDesigner:
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-3-sonnet-20240229")
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a React application architect. 
                Design component structure based on requirements.
                Return each component name on a new line.
                Use PascalCase for component names.
                Include only the component names without additional text."""),
            ("user", "Requirements:\n{requirements}")
        ])

    def design(self, requirements: List[str]) -> List[str]:
        requirements_text = "\n".join(requirements)
        chain = self.prompt | self.llm
        result = chain.invoke({"requirements": requirements_text})
        components = result.content.split("\n")
        return [comp.strip() for comp in components if comp.strip()]

def architecture_designer(state: dict) -> dict:
    designer = ArchitectureDesigner()
    components = designer.design(state["requirements"])
    new_state = {
        **state,
        "components": components,
        "requirements": state.get("requirements", []),
        "files": state.get("files", {}),
        "current_stage": "generation"
    }
    return new_state 