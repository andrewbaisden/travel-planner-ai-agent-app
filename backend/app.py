import os
import gradio as gr
from typing import Dict, List, Any
import logging
import ollama
import json


from agent import TravelAgent


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SimpleOllamaAgent:
    def __init__(self, model_name="llama3"):
        self.model_name = model_name
        logger.info(f"Initializing SimpleOllamaAgent with model: {model_name}")

    def run(self, prompt):
        try:
            logger.info(f"Generating with Ollama model: {self.model_name}")
            response = ollama.generate(model=self.model_name, prompt=prompt)
            return response['response']
        except Exception as e:
            logger.error(f"Error generating with Ollama: {e}")
            return "I'm sorry, I couldn't generate a response. Please try again."


def create_travel_plan(user_query, model_name="llama3"):

    logger.info("Starting travel plan creation...")

    try:

        try:
            logger.info(f"Using Ollama with model: {model_name}")

            try:
                response = ollama.list()
                logger.info(f"Ollama response: {response}")

                available_models = []

                if hasattr(response, 'models') and isinstance(response.models, list):

                    for model in response.models:
                        if hasattr(model, 'model'):
                            model_name_str = str(model.model)

                            if model_name_str.endswith(":latest"):
                                model_name_str = model_name_str.replace(
                                    ":latest", "")
                            available_models.append(model_name_str)
                elif isinstance(response, dict) and 'models' in response:

                    for model in response['models']:
                        if 'name' in model:
                            available_models.append(model['name'])

                logger.info(f"Available models: {available_models}")

                if model_name in available_models:
                    logger.info(f"Found requested model: {model_name}")

                    agent = SimpleOllamaAgent(model_name=model_name)

                elif available_models:
                    logger.warning(
                        f"Requested model {model_name} not found. Available models: {available_models}")
                    logger.info(
                        f"Using first available model: {available_models[0]}")
                    model_name = available_models[0]

                    agent = SimpleOllamaAgent(model_name=model_name)

                else:
                    logger.warning("No models available in Ollama")
                    raise Exception(
                        "No models available in Ollama. Please run 'ollama pull llama3' to download a model.")
            except Exception as e:
                logger.error(f"Error checking Ollama models: {e}")
                raise Exception(f"Error with Ollama: {e}")

        except Exception as e:
            logger.error(f"Error initializing Ollama model: {e}")
            logger.info("Falling back to fallback response...")
            raise e

        travel_plan = generate_travel_plan(agent, user_query)

        return travel_plan

    except Exception as e:
        logger.error(f"Error in create_travel_plan: {e}")

        fallback_text = f"""
        # Travel Plan (Fallback Mode)
        
        We encountered some issues while creating your travel plan.
        
        Based on your preferences: "{user_query}", please try again later or try with a different model.
        
        If the issue persists, make sure Ollama is properly installed and running.
        """

        return fallback_text


def create_travel_plan_agentic(user_query, model_name="llama3"):

    logger.info("Starting agentic travel plan creation...")

    try:

        try:
            logger.info(f"Using Ollama with model: {model_name}")

            try:
                response = ollama.list()
                logger.info(f"Ollama response: {response}")

                available_models = []

                if hasattr(response, 'models') and isinstance(response.models, list):

                    for model in response.models:
                        if hasattr(model, 'model'):
                            model_name_str = str(model.model)

                            if model_name_str.endswith(":latest"):
                                model_name_str = model_name_str.replace(
                                    ":latest", "")
                            available_models.append(model_name_str)
                elif isinstance(response, dict) and 'models' in response:

                    for model in response['models']:
                        if 'name' in model:
                            available_models.append(model['name'])

                logger.info(f"Available models: {available_models}")

                if model_name in available_models:
                    logger.info(f"Found requested model: {model_name}")

                    ollama_agent = SimpleOllamaAgent(model_name=model_name)

                elif available_models:
                    logger.warning(
                        f"Requested model {model_name} not found. Available models: {available_models}")
                    logger.info(
                        f"Using first available model: {available_models[0]}")
                    model_name = available_models[0]

                    ollama_agent = SimpleOllamaAgent(model_name=model_name)

                else:
                    logger.warning("No models available in Ollama")
                    raise Exception(
                        "No models available in Ollama. Please run 'ollama pull llama3' to download a model.")
            except Exception as e:
                logger.error(f"Error checking Ollama models: {e}")
                raise Exception(f"Error with Ollama: {e}")

        except Exception as e:
            logger.error(f"Error initializing Ollama model: {e}")
            logger.info("Falling back to fallback response...")
            raise e

        travel_agent = TravelAgent(ollama_agent, model_name=model_name)

        workflow_results = travel_agent.run_workflow(user_query)

        return workflow_results

    except Exception as e:
        logger.error(f"Error in create_travel_plan_agentic: {e}")

        fallback_text = f"""
        # Travel Plan (Fallback Mode)
        
        We encountered some issues while creating your travel plan.
        
        Based on your preferences: "{user_query}", please try again later or try with a different model.
        
        If the issue persists, make sure Ollama is properly installed and running.
        """

        return {
            "plan": {},
            "research": {},
            "initial_plan": fallback_text,
            "reflection": {},
            "final_plan": fallback_text
        }


def generate_travel_plan(agent, user_query):

    prompt = f"""
    You are a travel planning assistant. Create a detailed travel plan based on the following preferences:
    
    User Query: {user_query}
    
    Your travel plan should include:
    1. 2-3 recommended destinations that match the preferences
    2. For each destination, provide:
       - Best time to visit
       - Top attractions and activities
       - Accommodation recommendations
       - Local cuisine highlights
       - Travel tips
    
    Format your response as a well-structured travel plan with markdown formatting.
    """

    response = agent.run(prompt)

    if not response.strip().startswith("#"):
        response = "# Custom Travel Plan\n\n" + response

    return response


with gr.Blocks(title="Travel Planner") as demo:
    gr.Markdown("# Travel Planner Agent")
    gr.Markdown("""
    Enter your travel preferences and requirements, and the agent will create a travel plan for you.
    """)

    with gr.Row():
        user_input = gr.Textbox(
            label="Travel Preferences",
            placeholder="e.g., I want to visit warm places with beaches in December for a 7-day trip with my family. We enjoy outdoor activities and good food.",
            lines=5
        )

    default_models = ["llama3", "mistral", "gemma", "phi3"]
    try:
        response = ollama.list()
        available_models = []

        if hasattr(response, 'models') and isinstance(response.models, list):

            for model in response.models:
                if hasattr(model, 'model'):
                    model_name = str(model.model)

                    if model_name.endswith(":latest"):
                        model_name = model_name.replace(":latest", "")
                    available_models.append(model_name)
        elif isinstance(response, dict) and 'models' in response:

            for model in response['models']:
                if 'name' in model:
                    available_models.append(model['name'])

        if available_models:
            default_models = available_models
    except Exception as e:
        logger.warning(f"Could not get Ollama models: {e}")

    with gr.Row():
        model_dropdown = gr.Dropdown(
            label="Ollama Model",
            choices=default_models,
            value=default_models[0] if default_models else "llama3"
        )

    with gr.Row():
        workflow_type = gr.Radio(
            label="Workflow Type",
            choices=["Simple", "Agentic"],
            value="Simple"
        )

    submit_btn = gr.Button("Create Travel Plan")

    with gr.Row(visible=True) as simple_output_row:
        simple_output = gr.Markdown(label="Travel Plan")

    with gr.Row(visible=False) as agentic_output_row:
        with gr.Column():
            with gr.Accordion("Planning Phase", open=True):
                planning_output = gr.JSON(label="Identified Destinations")

            with gr.Accordion("Research Phase", open=True):
                research_output = gr.JSON(label="Destination Research")

        with gr.Column():
            with gr.Accordion("Initial Plan", open=True):
                initial_plan_output = gr.Markdown(label="Initial Travel Plan")

            with gr.Accordion("Reflection", open=True):
                reflection_output = gr.JSON(label="Plan Reflection")

            with gr.Accordion("Final Plan", open=True):
                final_plan_output = gr.Markdown(label="Final Travel Plan")

    def toggle_output_visibility(workflow):
        if workflow == "Simple":
            return gr.update(visible=True), gr.update(visible=False)
        else:
            return gr.update(visible=False), gr.update(visible=True)

    workflow_type.change(
        fn=toggle_output_visibility,
        inputs=[workflow_type],
        outputs=[simple_output_row, agentic_output_row]
    )

    def process_request(query, model, workflow):
        if not query.strip():
            if workflow == "Simple":
                return "Please enter your travel preferences", None, None, None, None, None
            else:
                return None, {}, {}, "Please enter your travel preferences", {}, ""

        try:
            if workflow == "Simple":
                result = create_travel_plan(query, model)
                return result, None, None, None, None, None
            else:
                workflow_results = create_travel_plan_agentic(query, model)
                return (
                    None,
                    workflow_results.get("plan", {}),
                    workflow_results.get("research", {}),
                    workflow_results.get("initial_plan", ""),
                    workflow_results.get("reflection", {}),
                    workflow_results.get("final_plan", "")
                )
        except Exception as e:
            logger.error(f"Error in process_request: {e}")
            error_message = f"An error occurred: {str(e)}"

            if workflow == "Simple":
                return error_message, None, None, None, None, None
            else:
                return None, {"error": str(e)}, {"error": str(e)}, error_message, {"error": str(e)}, error_message

    submit_btn.click(
        fn=process_request,
        inputs=[user_input, model_dropdown, workflow_type],
        outputs=[
            simple_output,
            planning_output,
            research_output,
            initial_plan_output,
            reflection_output,
            final_plan_output
        ]
    )

if __name__ == "__main__":

    import subprocess
    import sys

    try:

        try:
            response = ollama.list()
            logger.info(f"Ollama response: {response}")

            available_models = []

            if hasattr(response, 'models') and isinstance(response.models, list):

                for model in response.models:
                    if hasattr(model, 'model'):
                        model_name = str(model.model)

                        if model_name.endswith(":latest"):
                            model_name = model_name.replace(":latest", "")
                        available_models.append(model_name)
            elif isinstance(response, dict) and 'models' in response:

                for model in response['models']:
                    if 'name' in model:
                        available_models.append(model['name'])

            if available_models:
                logger.info(
                    f"Ollama is running with models: {', '.join(available_models)}")
                print(
                    f"\n✅ Ollama is running with available models: {', '.join(available_models)}")
            else:
                logger.warning("Ollama is running but no models are available")
                print(
                    "\n⚠️  Ollama is running but no models are available. Please pull a model:")
                print("   Run: ollama pull llama3")
        except Exception as e:
            logger.warning(f"Ollama might not be running: {e}")
            print(
                "\n⚠️  Warning: Ollama might not be running. Please make sure Ollama is installed and running.")
            print("   Install from: https://ollama.ai")
            print("   After installing, start Ollama and run: ollama pull llama3\n")
    except Exception as e:
        logger.error(f"Error checking Ollama: {e}")
        print(
            "\n⚠️  Error checking Ollama. Please make sure Ollama is installed and running.")
        print("   Install from: https://ollama.ai\n")

    demo.launch()
