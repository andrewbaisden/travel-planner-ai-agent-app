'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

type Model = string;
type WorkflowType = 'Simple' | 'Agentic';

interface TravelPlanResponse {
  travel_plan: string;
}

interface AgenticWorkflowResponse {
  plan: {
    destinations: string[];
    user_query: string;
  };
  research: Record<string, any>;
  initial_plan: string;
  reflection: {
    issues: string[];
    missing_info: string[];
    improvements: string[];
  };
  final_plan: string;
}

export default function Home() {
  const [userQuery, setUserQuery] = useState('');
  const [selectedModel, setSelectedModel] = useState<string>('llama3');
  const [workflowType, setWorkflowType] = useState<WorkflowType>('Simple');
  const [availableModels, setAvailableModels] = useState<Model[]>(['llama3']);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  // Results states
  const [simplePlan, setSimplePlan] = useState<string>('');
  const [planningOutput, setPlanningOutput] = useState<any>(null);
  const [researchOutput, setResearchOutput] = useState<any>(null);
  const [initialPlanOutput, setInitialPlanOutput] = useState<string>('');
  const [reflectionOutput, setReflectionOutput] = useState<any>(null);
  const [finalPlanOutput, setFinalPlanOutput] = useState<string>('');
  
  // Loading states for each step
  const [isSimpleLoading, setIsSimpleLoading] = useState(false);
  const [isPlanningLoading, setIsPlanningLoading] = useState(false);
  const [isResearchLoading, setIsResearchLoading] = useState(false);
  const [isInitialPlanLoading, setIsInitialPlanLoading] = useState(false);
  const [isReflectionLoading, setIsReflectionLoading] = useState(false);
  const [isFinalPlanLoading, setIsFinalPlanLoading] = useState(false);
  const [currentAgenticStep, setCurrentAgenticStep] = useState<string | null>(null);
  
  // Accordion states
  const [planningOpen, setPlanningOpen] = useState(true);
  const [researchOpen, setResearchOpen] = useState(true);
  const [initialPlanOpen, setInitialPlanOpen] = useState(true);
  const [reflectionOpen, setReflectionOpen] = useState(true);
  const [finalPlanOpen, setFinalPlanOpen] = useState(true);

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const response = await axios.get('http://localhost:8000/models');
        if (response.data.models && response.data.models.length > 0) {
          setAvailableModels(response.data.models);
          setSelectedModel(response.data.models[0]);
        }
      } catch (err) {
        console.error('Error fetching models:', err);
    
        setAvailableModels(['llama3', 'mistral', 'gemma', 'phi3']);
      }
    };

    fetchModels();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!userQuery.trim()) {
      setError('Please enter your travel preferences');
      return;
    }
    
    setIsLoading(true);
    setError(null);
    
    // Reset all outputs
    setSimplePlan('');
    setPlanningOutput(null);
    setResearchOutput(null);
    setInitialPlanOutput('');
    setReflectionOutput(null);
    setFinalPlanOutput('');
    
    if (workflowType === 'Simple') {
      // Set simple loading state
      setIsSimpleLoading(true);
    } else {
      // Set initial agentic loading states
      setIsPlanningLoading(true);
      setCurrentAgenticStep('Planning');
    }
    
    try {
      if (workflowType === 'Simple') {
        const response = await axios.post('http://localhost:8000/travel-plan-unified', {
          user_query: userQuery,
          model_name: selectedModel,
          workflow_type: workflowType
        });
        
        const data = response.data as TravelPlanResponse;
        setSimplePlan(data.travel_plan);
      } else {

        setIsPlanningLoading(true);
        setCurrentAgenticStep('Planning');
        
  
        const responsePromise = axios.post('http://localhost:8000/travel-plan-unified', {
          user_query: userQuery,
          model_name: selectedModel,
          workflow_type: workflowType
        });
        
   
        await new Promise(resolve => setTimeout(resolve, 2000));
        setIsPlanningLoading(false);
        
        // Research phase
        setIsResearchLoading(true);
        setCurrentAgenticStep('Research');
        await new Promise(resolve => setTimeout(resolve, 2000));
        setIsResearchLoading(false);
        
        // Initial plan phase
        setIsInitialPlanLoading(true);
        setCurrentAgenticStep('Initial Plan');
        await new Promise(resolve => setTimeout(resolve, 2000));
        setIsInitialPlanLoading(false);
        
        // Reflection phase
        setIsReflectionLoading(true);
        setCurrentAgenticStep('Reflection');
        await new Promise(resolve => setTimeout(resolve, 2000));
        setIsReflectionLoading(false);
        
        // Final plan phase
        setIsFinalPlanLoading(true);
        setCurrentAgenticStep('Final Plan');
        await new Promise(resolve => setTimeout(resolve, 2000));
        
   
        const response = await responsePromise;
        const data = response.data as AgenticWorkflowResponse;
        
        // Update all outputs
        setPlanningOutput(data.plan);
        setResearchOutput(data.research);
        setInitialPlanOutput(data.initial_plan);
        setReflectionOutput(data.reflection);
        setFinalPlanOutput(data.final_plan);
        setIsFinalPlanLoading(false);
        setCurrentAgenticStep(null);
      }
    } catch (err: any) {
      console.error('Error creating travel plan:', err);
      setError(err.response?.data?.detail || 'An error occurred while creating your travel plan');
    } finally {
      setIsLoading(false);
      setIsSimpleLoading(false);
      setIsPlanningLoading(false);
      setIsResearchLoading(false);
      setIsInitialPlanLoading(false);
      setIsReflectionLoading(false);
      setIsFinalPlanLoading(false);
      setCurrentAgenticStep(null);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-4xl">
      <h1 className="text-3xl font-bold text-center mb-8 text-white">Travel Planner Agent</h1>
      
      <div className="bg-white rounded-lg shadow-md p-6 mb-8">
        <p className="mb-4">
          Enter your travel preferences and requirements, and the agent will create a travel plan for you.
        </p>
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="user-input" className="block text-sm font-medium text-gray-700 mb-1">
              Travel Preferences
            </label>
            <textarea
              id="user-input"
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
              rows={5}
              placeholder="I'm looking for a 7-day trip to a warm destination with beaches, good food, and cultural experiences. My budget is around $2000."
              value={userQuery}
              onChange={(e) => setUserQuery(e.target.value)}
            />
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label htmlFor="model-dropdown" className="block text-sm font-medium text-gray-700 mb-1">
                Model
              </label>
              <select
                id="model-dropdown"
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-primary focus:border-primary"
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
              >
                {availableModels.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Workflow Type
              </label>
              <div className="flex space-x-4">
                <label className="inline-flex items-center">
                  <input
                    type="radio"
                    className="form-radio text-primary"
                    name="workflow-type"
                    value="Simple"
                    checked={workflowType === 'Simple'}
                    onChange={() => setWorkflowType('Simple')}
                  />
                  <span className="ml-2">Simple</span>
                </label>
                <label className="inline-flex items-center">
                  <input
                    type="radio"
                    className="form-radio text-primary"
                    name="workflow-type"
                    value="Agentic"
                    checked={workflowType === 'Agentic'}
                    onChange={() => setWorkflowType('Agentic')}
                  />
                  <span className="ml-2">Agentic</span>
                </label>
              </div>
            </div>
          </div>
          
          <button
            type="submit"
            className="w-full bg-indigo-500 hover:bg-indigo-800 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline transition duration-150 ease-in-out"
            disabled={isLoading}
          >
            {isLoading ? 'Creating Travel Plan...' : 'Create Travel Plan'}
          </button>
        </form>
        
        {error && (
          <div className="mt-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}
      </div>
      

      {workflowType === 'Simple' && (
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-bold mb-4">Travel Plan</h2>
          {isSimpleLoading ? (
            <div className="flex flex-col items-center justify-center py-8">
              <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              <p className="mt-4 text-gray-700 font-medium">Creating your travel plan...</p>
            </div>
          ) : simplePlan ? (
            <div className="markdown-content">
              <ReactMarkdown>{simplePlan}</ReactMarkdown>
            </div>
          ) : null}
        </div>
      )}
      

      {workflowType === 'Agentic' && (
        <>
   
          <div className="bg-white rounded-lg shadow-md p-6 mb-4">
            <div 
              className="flex justify-between items-center cursor-pointer" 
              onClick={() => setPlanningOpen(!planningOpen)}
            >
              <div className="flex items-center">
                <h2 className="text-xl font-bold">Planning</h2>
                {isPlanningLoading && (
                  <div className="ml-3 w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                )}
                {currentAgenticStep === 'Planning' && (
                  <span className="ml-3 bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">Active</span>
                )}
              </div>
              <span>{planningOpen ? '▼' : '►'}</span>
            </div>
            <div className={`accordion-content ${planningOpen ? 'open' : ''}`}>
              {planningOutput ? (
                <div className="mt-4">
                  <h3 className="font-semibold">User Query:</h3>
                  <p className="mb-2">{planningOutput.user_query}</p>
                  
                  <h3 className="font-semibold mt-4">Identified Destinations:</h3>
                  <ul className="list-disc pl-5">
                    {planningOutput.destinations?.map((dest: string, index: number) => (
                      <li key={index}>{dest}</li>
                    ))}
                  </ul>
                </div>
              ) : isPlanningLoading ? (
                <div className="flex justify-center py-8">
                  <p className="text-gray-500">Analyzing your travel preferences...</p>
                </div>
              ) : null}
            </div>
          </div>
          
 
          <div className="bg-white rounded-lg shadow-md p-6 mb-4">
            <div 
              className="flex justify-between items-center cursor-pointer" 
              onClick={() => setResearchOpen(!researchOpen)}
            >
              <div className="flex items-center">
                <h2 className="text-xl font-bold">Research</h2>
                {isResearchLoading && (
                  <div className="ml-3 w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                )}
                {currentAgenticStep === 'Research' && (
                  <span className="ml-3 bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">Active</span>
                )}
              </div>
              <span>{researchOpen ? '▼' : '►'}</span>
            </div>
            <div className={`accordion-content ${researchOpen ? 'open' : ''}`}>
              {researchOutput ? (
                <div className="mt-4">
                  {Object.entries(researchOutput).map(([location, info]: [string, any]) => (
                    <div key={location} className="mb-6">
                      <h3 className="text-lg font-bold">{location}</h3>
                      
                      <div className="mt-2">
                        <h4 className="font-semibold">Best Time to Visit:</h4>
                        <p>{info.best_time}</p>
                      </div>
                      
                      <div className="mt-2">
                        <h4 className="font-semibold">Top Attractions:</h4>
                        <ul className="list-disc pl-5">
                          {Array.isArray(info.attractions) ? 
                            info.attractions.map((attraction: string, i: number) => (
                              <li key={i}>{attraction}</li>
                            )) : 
                            <li>{info.attractions}</li>
                          }
                        </ul>
                      </div>
                      
                      <div className="mt-2">
                        <h4 className="font-semibold">Accommodation:</h4>
                        <ul className="list-disc pl-5">
                          {Array.isArray(info.accommodation) ? 
                            info.accommodation.map((acc: string, i: number) => (
                              <li key={i}>{acc}</li>
                            )) : 
                            <li>{info.accommodation}</li>
                          }
                        </ul>
                      </div>
                      
                      <div className="mt-2">
                        <h4 className="font-semibold">Cuisine:</h4>
                        <ul className="list-disc pl-5">
                          {Array.isArray(info.cuisine) ? 
                            info.cuisine.map((dish: string, i: number) => (
                              <li key={i}>{dish}</li>
                            )) : 
                            <li>{info.cuisine}</li>
                          }
                        </ul>
                      </div>
                      
                      <div className="mt-2">
                        <h4 className="font-semibold">Travel Tips:</h4>
                        <ul className="list-disc pl-5">
                          {Array.isArray(info.tips) ? 
                            info.tips.map((tip: string, i: number) => (
                              <li key={i}>{tip}</li>
                            )) : 
                            <li>{info.tips}</li>
                          }
                        </ul>
                      </div>
                    </div>
                  ))}
                </div>
              ) : isResearchLoading ? (
                <div className="flex justify-center py-8">
                  <p className="text-gray-500">Researching destinations...</p>
                </div>
              ) : null}
            </div>
          </div>
          
  
          <div className="bg-white rounded-lg shadow-md p-6 mb-4">
            <div 
              className="flex justify-between items-center cursor-pointer" 
              onClick={() => setInitialPlanOpen(!initialPlanOpen)}
            >
              <div className="flex items-center">
                <h2 className="text-xl font-bold">Initial Travel Plan</h2>
                {isInitialPlanLoading && (
                  <div className="ml-3 w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                )}
                {currentAgenticStep === 'Initial Plan' && (
                  <span className="ml-3 bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">Active</span>
                )}
              </div>
              <span>{initialPlanOpen ? '▼' : '►'}</span>
            </div>
            <div className={`accordion-content ${initialPlanOpen ? 'open' : ''}`}>
              {initialPlanOutput ? (
                <div className="mt-4 markdown-content">
                  <ReactMarkdown>{initialPlanOutput}</ReactMarkdown>
                </div>
              ) : isInitialPlanLoading ? (
                <div className="flex justify-center py-8">
                  <p className="text-gray-500">Creating initial travel plan...</p>
                </div>
              ) : null}
            </div>
          </div>
          
  
          <div className="bg-white rounded-lg shadow-md p-6 mb-4">
            <div 
              className="flex justify-between items-center cursor-pointer" 
              onClick={() => setReflectionOpen(!reflectionOpen)}
            >
              <div className="flex items-center">
                <h2 className="text-xl font-bold">Reflection</h2>
                {isReflectionLoading && (
                  <div className="ml-3 w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                )}
                {currentAgenticStep === 'Reflection' && (
                  <span className="ml-3 bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">Active</span>
                )}
              </div>
              <span>{reflectionOpen ? '▼' : '►'}</span>
            </div>
            <div className={`accordion-content ${reflectionOpen ? 'open' : ''}`}>
              {reflectionOutput ? (
                <div className="mt-4">
                  {reflectionOutput.issues && reflectionOutput.issues.length > 0 && (
                    <div className="mb-4">
                      <h3 className="font-semibold">Issues:</h3>
                      <ul className="list-disc pl-5">
                        {reflectionOutput.issues.map((issue: string, i: number) => (
                          <li key={i}>{issue}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {reflectionOutput.missing_info && reflectionOutput.missing_info.length > 0 && (
                    <div className="mb-4">
                      <h3 className="font-semibold">Missing Information:</h3>
                      <ul className="list-disc pl-5">
                        {reflectionOutput.missing_info.map((info: string, i: number) => (
                          <li key={i}>{info}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {reflectionOutput.improvements && reflectionOutput.improvements.length > 0 && (
                    <div className="mb-4">
                      <h3 className="font-semibold">Suggested Improvements:</h3>
                      <ul className="list-disc pl-5">
                        {reflectionOutput.improvements.map((improvement: string, i: number) => (
                          <li key={i}>{improvement}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              ) : isReflectionLoading ? (
                <div className="flex justify-center py-8">
                  <p className="text-gray-500">Reflecting on the travel plan...</p>
                </div>
              ) : null}
            </div>
          </div>
          
  
          <div className="bg-white rounded-lg shadow-md p-6 mb-4">
            <div 
              className="flex justify-between items-center cursor-pointer" 
              onClick={() => setFinalPlanOpen(!finalPlanOpen)}
            >
              <div className="flex items-center">
                <h2 className="text-xl font-bold">Final Travel Plan</h2>
                {isFinalPlanLoading && (
                  <div className="ml-3 w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                )}
                {currentAgenticStep === 'Final Plan' && (
                  <span className="ml-3 bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">Active</span>
                )}
              </div>
              <span>{finalPlanOpen ? '▼' : '►'}</span>
            </div>
            <div className={`accordion-content ${finalPlanOpen ? 'open' : ''}`}>
              {finalPlanOutput ? (
                <div className="mt-4 markdown-content">
                  <ReactMarkdown>{finalPlanOutput}</ReactMarkdown>
                </div>
              ) : isFinalPlanLoading ? (
                <div className="flex justify-center py-8">
                  <p className="text-gray-500">Finalizing your travel plan...</p>
                </div>
              ) : null}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
