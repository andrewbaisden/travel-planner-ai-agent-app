from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
import ollama
import json


from agent import TravelAgent
from app import SimpleOllamaAgent


logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


app = FastAPI(title="Travel Planner API",
              description="API for the Travel Planner application",
              version="1.0.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class TravelPlanRequest(BaseModel):
    user_query: str
    model_name: str = "llama3"
    workflow_type: str = "Simple"


class TravelPlanResponse(BaseModel):
    travel_plan: str


class AgenticWorkflowResponse(BaseModel):
    plan: Dict[str, Any]
    research: Dict[str, Any]
    initial_plan: str
    reflection: Dict[str, Any]
    final_plan: str

# API endpoints


@app.get("/")
async def root():
    return {"message": "Travel Planner API is running"}


@app.get("/models")
async def get_models():

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

        if not available_models:

            available_models = ["llama3", "mistral", "gemma", "phi3"]

        return {"models": available_models}
    except Exception as e:
        logger.error(f"Error getting models: {e}")

        return {"models": ["llama3", "mistral", "gemma", "phi3"]}


@app.post("/travel-plan", response_model=TravelPlanResponse)
async def create_travel_plan(request: TravelPlanRequest):

    try:
        from app import create_travel_plan
        travel_plan = create_travel_plan(
            request.user_query, request.model_name)
        return {"travel_plan": travel_plan}
    except Exception as e:
        logger.error(f"Error creating travel plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/travel-plan-agentic", response_model=AgenticWorkflowResponse)
async def create_travel_plan_agentic(request: TravelPlanRequest):

    try:
        from app import create_travel_plan_agentic
        workflow_results = create_travel_plan_agentic(
            request.user_query, request.model_name)
        return workflow_results
    except Exception as e:
        logger.error(f"Error creating agentic travel plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/travel-plan-unified")
async def create_travel_plan_unified(request: TravelPlanRequest):

    try:
        if request.workflow_type == "Simple":
            from app import create_travel_plan
            travel_plan = create_travel_plan(
                request.user_query, request.model_name)
            return {"travel_plan": travel_plan}
        else:
            from app import create_travel_plan_agentic
            workflow_results = create_travel_plan_agentic(
                request.user_query, request.model_name)
            return workflow_results
    except Exception as e:
        logger.error(f"Error creating travel plan: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
