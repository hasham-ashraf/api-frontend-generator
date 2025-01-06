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
        print(f"\n=== REACT GENERATOR: Generating {component} ===")
        print(f"Component: {component}")
        print(f"Requirements: {requirements}")
        chain = self.component_prompt | self.llm
        result = chain.invoke({
            "component": component,
            "requirements": "\n".join(requirements)
        })
        print(f"Generated code length: {len(result.content)} characters")
        print("===============================\n")
        return result.content

    def generate_app(self, components: list) -> str:
        print("\n=== REACT GENERATOR: Generating App.jsx ===")
        print(f"Components to include: {components}")
        imports = "\n".join([
            f"import {comp} from './components/{comp}';"
            for comp in components
        ])
        
        app_code = f"""
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
        print(f"Generated App.jsx code length: {len(app_code)} characters")
        print("====================================\n")
        return app_code

def react_generator(state: dict) -> dict:
    print("\n=== REACT GENERATOR STATE UPDATE ===")
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
    
    print(f"Generated {len(files)} files:")
    for path in files.keys():
        print(f"- {path}")
    
    new_state = {
        **state,
        "files": files,
        "requirements": state.get("requirements", []),
        "components": state.get("components", []),
        "current_stage": "complete"
    }
    print("================================\n")
    return new_state 