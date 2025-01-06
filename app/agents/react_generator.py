from typing import Dict
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

class ReactGenerator:
    def __init__(self):
        self.llm = ChatAnthropic(model="claude-3-sonnet-20240229")
        self.component_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a React component generator.
                Generate a modern React component using the following guidelines:
                - Use functional components with hooks
                - Include proper TypeScript types
                - Use Tailwind CSS for styling
                - Implement proper error handling
                - Add JSDoc comments for documentation
                Return only the component code without any explanation."""),
            ("user", "Component: {component}\nRequirements: {requirements}")
        ])

    def generate_component(self, component: str, requirements: list) -> str:
        chain = self.component_prompt | self.llm
        result = chain.invoke({
            "component": component,
            "requirements": "\n".join(requirements)
        })
        return result.content

    def generate_app(self, components: list) -> str:
        imports = "\n".join([
            f"import {comp} from './components/{comp}';"
            for comp in components
        ])
        
        return f"""
import React from 'react';
{imports}

export default function App() {{
    return (
        <div className="min-h-screen bg-gray-100">
            {" ".join([f"<{comp} />" for comp in components])}
        </div>
    );
}}
"""

def react_generator(state: dict) -> dict:
    generator = ReactGenerator()
    files = {}
    
    # Generate App.jsx
    files["src/App.jsx"] = generator.generate_app(state["components"])
    
    # Generate individual components
    for component in state["components"]:
        files[f"src/components/{component}.jsx"] = generator.generate_component(
            component,
            state["requirements"]
        )
        
    # Create a new state dictionary with all required fields
    new_state = {
        **state,
        "files": files,
        "requirements": state.get("requirements", []),
        "components": state.get("components", []),
        "current_stage": "complete"
    }
    return new_state 