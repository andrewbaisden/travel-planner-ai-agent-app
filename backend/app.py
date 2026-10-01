import gradio as gr
import logging


from agent import TravelAgent
from llm import SimpleOllamaAgent, create_language_model, list_models, list_ollama_models


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def _fallback_plan(user_query: str) -> str:
    return f"""
        # Travel Plan (Fallback Mode)
        
        We encountered some issues while creating your travel plan.
        
        Based on your preferences: "{user_query}", please try again later or try with a different model.
        
        Ollama is the default runtime. For a Groq model, set GROQ_API_KEY in .env and pick a name that starts with groq:.
        """


def create_travel_plan(user_query, model_name="llama3"):

    logger.info("Starting travel plan creation with model: %s", model_name)

    try:
        agent = create_language_model(model_name)
        return generate_travel_plan(agent, user_query)
    except Exception as e:
        logger.error(f"Error in create_travel_plan: {e}")
        return _fallback_plan(user_query)


def create_travel_plan_agentic(user_query, model_name="llama3"):

    logger.info("Starting agentic travel plan creation with model: %s", model_name)

    try:
        agent = create_language_model(model_name)
        travel_agent = TravelAgent(agent, model_name=agent.model_name)
        return travel_agent.run_workflow(user_query)
    except Exception as e:
        logger.error(f"Error in create_travel_plan_agentic: {e}")
        fallback_text = _fallback_plan(user_query)
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

    default_models = list_models()

    with gr.Row():
        model_dropdown = gr.Dropdown(
            label="Model",
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
        available_models = list_ollama_models()
        if available_models:
            logger.info(
                "Ollama is running with models: %s", ", ".join(available_models))
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

    demo.launch()
