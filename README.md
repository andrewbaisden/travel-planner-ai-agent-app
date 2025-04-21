# Travel Planner Application

This application uses Ollama to help users plan their travels. It uses local language models to generate detailed travel plans based on user preferences.

## Features

- **Local Model Execution**: Uses Ollama to run models locally on your machine
- **Template-Based Generation**: Creates structured travel plans with destinations, attractions, and tips
- **Flexible Model Selection**: Choose from any model available in your Ollama installation
- **Agentic Workflow**: Optional AI agent workflow that breaks down travel planning into distinct phases
- **Multiple Frontends**: Choose between Gradio UI or a modern React frontend built with Next.js

## Tools Used

- Ollama API for local model execution
- Gradio for the original user interface
- FastAPI for the backend API
- Next.js and React for the modern frontend

## How It Works

The Travel Planner application offers two workflow options:

### Simple Workflow

1. **Model Selection**: The application checks for available models in your Ollama installation and allows you to select one.
2. **User Input Processing**: Your travel preferences are sent to the selected Ollama model.
3. **Template-Based Generation**: The application uses a carefully designed prompt template to guide the model in creating a structured travel plan.
4. **Response Formatting**: The generated travel plan is formatted with proper markdown for easy reading.

### Agentic Workflow

The agentic workflow breaks down the travel planning process into distinct phases:

1. **Planning Phase**: Analyzes your query and identifies potential destinations that match your preferences.
2. **Research Phase**: Gathers detailed information about each identified destination.
3. **Generation Phase**: Creates an initial travel plan based on the collected information.
4. **Reflection Phase**: Reviews the travel plan to identify any issues or missing information.
5. **Improvement Phase**: Enhances the travel plan to address any identified issues.

The agentic approach provides more detailed and thoughtful travel plans by acting how a human travel agent would act when approaching the task.

## Installation

### 1.  Clone this repository

Run this command in your terminal and clone this Git repository somewhere on your local machine, like the desktop or documents, for example:

```shell
git clone https://github.com/andrewbaisden/travel-planner-ai-agent-app.git
cd travel-planner-ai-agent-app
```

You should now have an identical copy of this repo on your computer.

### 2. Set up the backend

The next thing we need to do is set up our Python and FastAPI backend so in the root directory of  the `travel-planner-ai-agent-app` folder, run these commands:

> Depending on your setup your might need to use either the `python` or `python3` command.

```shell
# Create a Python virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate

# Install Python dependencies
pip3 install -r requirements.txt

# Change into the backend folder
cd backend

# Start the FastAPI servers
python3 api.py # Run the FastAPI API server
python3 app.py # Run the Gradio frontend
```

These commands create a Python virtual environment, install the Python dependencies and get our backend servers running. We have a Fastapi server which has the endpoints for our frontend to use. And we also have a Gradio interface for connecting to our backend, which is good for demos.

### 3. Set up the frontend

Lastly, let's get our React frontend up and running. Run these commands to complete the setup process:

```shell
# Navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the development server
npm run dev
```

Our application should be fully working.

### 4. Running the Python Backend

Here are the relevant URLS and details for our backend.

API LLM Models: http://127.0.0.1:11434/api/tags
Gradio interface for Travel Planner Agent: http://127.0.0.1:7860/

Here you can see what our Gradio interface looks like:

![Gradio interface simple mode](https://res.cloudinary.com/d74fh3kw/image/upload/v1744908685/Gradio_Travel_Planner_Agent_App_Simple_Mode_vjbwlu.png)

This is what our Gradio interface looks like in simple mode.

![Gradio interface agentic mode](https://res.cloudinary.com/d74fh3kw/image/upload/v1744908685/Gradio_Travel_Planner_Agent_App_Agentic_Mode_j9jmcz.png)

And this is what our Gradio interface looks like in agentic mode.

### 5. Running the React Frontend

And here are the relevant URLS and details for our frontend.

Next.js Travel Planner Agent app frontend: http://localhost:3000/

Here you can see what our React application looks like:

![React app simple mode](https://res.cloudinary.com/d74fh3kw/image/upload/v1744909120/React_Travel_Planner_Agent_App_Simple_Mode_qraybr.png)

This is what our React app looks like in simple mode.

![React app agentic mode](https://res.cloudinary.com/d74fh3kw/image/upload/v1744909121/React_Travel_Planner_Agent_App_Agentic_Mode_hzvm1c.png)

This is what our React app looks like in agentic mode.

In theory, this application can work with various vendors' LLMS. However, I found it performs best with the Llama models (e.g., Llama 3.1, Llama 3.2).

One important thing to note is that generating a travel plan locally can be a bit slow, depending on your computer’s performance. That’s because you’re running these LLMS directly on your machine, not through cloud-based services. Unlike online LLM platforms, which run on powerful servers built to handle thousands of requests at once, your local setup is limited by your device’s hardware.

On my M1 MacBook Pro, the simple workflow generated a plan in about 1 - 2 minutes, while the agentic workflow took over 3 minutes to achieve the same result.

Of course, this is just a demo app and not meant for production, so those times are acceptable for testing and experimentation.

## Usage

1. Ensure Ollama is running on your machine
2. Enter your travel preferences and requirements in the text box
3. Select an Ollama model from the dropdown menu
4. Choose between Simple or Agentic workflow
5. Click "Create Travel Plan" to generate your personalized travel plan
6. For the agentic workflow, you can explore each phase of the planning process in the accordions

## Example Prompts

- "I want to visit warm places with beaches in December for a 7-day trip with my family. We enjoy outdoor activities and good food."
- "Looking for a budget-friendly European city tour in spring, focusing on historical sites and local cuisine."
- "Planning a solo hiking trip to national parks in the western US for two weeks in summer."

## Requirements

- Python 3.8+
- Ollama installed and running
- Internet connection (only for initial model download)
- Node.js and npm (for React frontend)

## Troubleshooting

- **Ollama Not Running**: Make sure Ollama is installed and running on your machine. The application will display a warning if it cannot connect to Ollama.
- **No Models Available**: If you see a message that no models are available, run `ollama pull llama3` to download the recommended model.
- **Model Not Found**: If your requested model is not found, the application will automatically use the first available model in your Ollama installation.
- **FastAPI Backend Not Running**: Make sure the FastAPI backend is running before starting the React frontend.

## Technical Details

### Agentic Architecture

The agentic workflow is implemented using a `TravelAgent` class that orchestrates the following components:

- **Tool Functions**: Specialized functions for identifying locations, researching destinations, and generating travel plans.
- **Memory System**: Maintains context between different phases of the workflow.
- **Reflection Mechanism**: Evaluates the quality of the generated travel plan and identifies areas for improvement.

The agent uses a series of carefully crafted prompts to guide the language model through each phase of the travel planning process.

### Frontend Architecture

The application offers two frontend options:

1. **Gradio UI**: A simple and functional interface built with Gradio, ideal for quick use and testing.
2. **React Frontend**: A modern, responsive UI built with Next.js and TailwindCSS, providing a more polished user experience.

### Backend Architecture

- **FastAPI Backend**: Provides RESTful API endpoints for the React frontend to interact with the travel planning functionality.
- **Direct Python Integration**: The Gradio UI interacts directly with the Python functions without going through the API.


