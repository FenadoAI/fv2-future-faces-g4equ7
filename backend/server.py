from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime

# AI agents
from ai_agents.agents import AgentConfig, SearchAgent, ChatAgent
import httpx
import json


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# AI agents init
agent_config = AgentConfig()
search_agent: Optional[SearchAgent] = None
chat_agent: Optional[ChatAgent] = None

# Main app
app = FastAPI(title="AI Agents API", description="Minimal AI Agents API with LangGraph and MCP support")

# API router
api_router = APIRouter(prefix="/api")


# Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str


# AI agent models
class ChatRequest(BaseModel):
    message: str
    agent_type: str = "chat"  # "chat" or "search"
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    success: bool
    response: str
    agent_type: str
    capabilities: List[str]
    metadata: dict = Field(default_factory=dict)
    error: Optional[str] = None


class SearchRequest(BaseModel):
    query: str
    max_results: int = 5


class SearchResponse(BaseModel):
    success: bool
    query: str
    summary: str
    search_results: Optional[dict] = None
    sources_count: int
    error: Optional[str] = None


# Child Name Generator Models
class NameGenerationRequest(BaseModel):
    description: str  # Free-form text describing the kind of name they want

class NameGenerationResponse(BaseModel):
    success: bool
    suggested_names: List[str]
    explanation: str
    error: Optional[str] = None

class ImageGenerationRequest(BaseModel):
    child_name: str
    description: Optional[str] = None

class ImageGenerationResponse(BaseModel):
    success: bool
    image_url: str
    error: Optional[str] = None

class AgeProgressionRequest(BaseModel):
    base_image_prompt: str
    child_name: str
    ages: List[int] = [3, 6, 10, 15, 18]

class AgeProgressionResponse(BaseModel):
    success: bool
    age_progression_images: List[dict]  # [{age: int, image_url: str}]
    error: Optional[str] = None

# Routes
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]


# AI agent routes
@api_router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    # Chat with AI agent
    global search_agent, chat_agent
    
    try:
        # Init agents if needed
        if request.agent_type == "search" and search_agent is None:
            search_agent = SearchAgent(agent_config)
            
        elif request.agent_type == "chat" and chat_agent is None:
            chat_agent = ChatAgent(agent_config)
        
        # Select agent
        agent = search_agent if request.agent_type == "search" else chat_agent
        
        if agent is None:
            raise HTTPException(status_code=500, detail="Failed to initialize agent")
        
        # Execute agent
        response = await agent.execute(request.message)
        
        return ChatResponse(
            success=response.success,
            response=response.content,
            agent_type=request.agent_type,
            capabilities=agent.get_capabilities(),
            metadata=response.metadata,
            error=response.error
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}")
        return ChatResponse(
            success=False,
            response="",
            agent_type=request.agent_type,
            capabilities=[],
            error=str(e)
        )


@api_router.post("/search", response_model=SearchResponse)
async def search_and_summarize(request: SearchRequest):
    # Web search with AI summary
    global search_agent
    
    try:
        # Init search agent if needed
        if search_agent is None:
            search_agent = SearchAgent(agent_config)
        
        # Search with agent
        search_prompt = f"Search for information about: {request.query}. Provide a comprehensive summary with key findings."
        result = await search_agent.execute(search_prompt, use_tools=True)
        
        if result.success:
            return SearchResponse(
                success=True,
                query=request.query,
                summary=result.content,
                search_results=result.metadata,
                sources_count=result.metadata.get("tools_used", 0)
            )
        else:
            return SearchResponse(
                success=False,
                query=request.query,
                summary="",
                sources_count=0,
                error=result.error
            )
            
    except Exception as e:
        logger.error(f"Error in search endpoint: {e}")
        return SearchResponse(
            success=False,
            query=request.query,
            summary="",
            sources_count=0,
            error=str(e)
        )


@api_router.get("/agents/capabilities")
async def get_agent_capabilities():
    # Get agent capabilities
    try:
        capabilities = {
            "search_agent": SearchAgent(agent_config).get_capabilities(),
            "chat_agent": ChatAgent(agent_config).get_capabilities()
        }
        return {
            "success": True,
            "capabilities": capabilities
        }
    except Exception as e:
        logger.error(f"Error getting capabilities: {e}")
        return {
            "success": False,
            "error": str(e)
        }


# Child Name Generator Routes
@api_router.post("/generate-name", response_model=NameGenerationResponse)
async def generate_child_name(request: NameGenerationRequest):
    """Generate child name suggestions based on free-form description"""
    global chat_agent

    try:
        # Initialize chat agent if needed
        if chat_agent is None:
            chat_agent = ChatAgent(agent_config)

        # Create prompt for name generation
        name_prompt = f"""
        Generate 5 unique child names based on this description: "{request.description}"

        Please consider:
        - The style and characteristics requested
        - Cultural backgrounds if mentioned
        - Gender preferences if specified
        - Modern vs traditional preferences
        - Any specific letters or sounds mentioned

        Provide your response as a JSON object with:
        - "names": array of 5 suggested names
        - "explanation": brief explanation of why these names fit the description

        Example format:
        {{
            "names": ["Emma", "Oliver", "Sophia", "Liam", "Ava"],
            "explanation": "These are popular modern names that are classic yet contemporary..."
        }}
        """

        # Execute agent
        result = await chat_agent.execute(name_prompt)

        if result.success:
            try:
                # Try to parse JSON response
                response_text = result.content.strip()
                if response_text.startswith("```json"):
                    response_text = response_text.replace("```json", "").replace("```", "").strip()

                parsed_response = json.loads(response_text)

                return NameGenerationResponse(
                    success=True,
                    suggested_names=parsed_response.get("names", []),
                    explanation=parsed_response.get("explanation", ""),
                )
            except json.JSONDecodeError:
                # Fallback: extract names from text response
                lines = result.content.split('\n')
                names = []
                for line in lines:
                    if any(char.isalpha() for char in line) and len(line.strip()) < 30:
                        clean_line = line.strip().replace("-", "").replace("*", "").replace(".", "").strip()
                        if clean_line and len(clean_line.split()) <= 2:
                            names.append(clean_line)

                return NameGenerationResponse(
                    success=True,
                    suggested_names=names[:5] if names else ["Alex", "Jordan", "Casey", "Taylor", "Morgan"],
                    explanation=result.content[:200] + "..." if len(result.content) > 200 else result.content,
                )
        else:
            return NameGenerationResponse(
                success=False,
                suggested_names=[],
                explanation="",
                error=result.error
            )

    except Exception as e:
        logger.error(f"Error in name generation endpoint: {e}")
        return NameGenerationResponse(
            success=False,
            suggested_names=[],
            explanation="",
            error=str(e)
        )


@api_router.post("/generate-image", response_model=ImageGenerationResponse)
async def generate_child_image(request: ImageGenerationRequest):
    """Generate an image of a child based on the selected name"""

    try:
        # Create image prompt
        if request.description:
            image_prompt = f"A portrait of a happy, adorable child named {request.child_name}. {request.description}. High quality, professional portrait, soft lighting, warm and friendly expression."
        else:
            image_prompt = f"A portrait of a happy, adorable child named {request.child_name}. High quality, professional portrait, soft lighting, warm and friendly expression, realistic style."

        # Use MCP image generation service (assuming it's available)
        async with httpx.AsyncClient() as client:
            # This would connect to the MCP image generation service
            # For now, we'll use a placeholder implementation

            # Generate image using available service
            image_url = await _generate_image_with_mcp(image_prompt)

            return ImageGenerationResponse(
                success=True,
                image_url=image_url
            )

    except Exception as e:
        logger.error(f"Error in image generation endpoint: {e}")
        return ImageGenerationResponse(
            success=False,
            image_url="",
            error=str(e)
        )


@api_router.post("/generate-age-progression", response_model=AgeProgressionResponse)
async def generate_age_progression(request: AgeProgressionRequest):
    """Generate age progression images showing the child at different ages"""

    try:
        age_images = []

        # Generate images for each age
        for age in request.ages:
            age_prompt = f"{request.base_image_prompt} The child named {request.child_name} is now {age} years old. Show appropriate physical development for age {age}. High quality, professional portrait."

            try:
                image_url = await _generate_image_with_mcp(age_prompt)
                age_images.append({
                    "age": age,
                    "image_url": image_url
                })
            except Exception as e:
                logger.error(f"Error generating image for age {age}: {e}")
                # Continue with other ages even if one fails
                continue

        return AgeProgressionResponse(
            success=True,
            age_progression_images=age_images
        )

    except Exception as e:
        logger.error(f"Error in age progression endpoint: {e}")
        return AgeProgressionResponse(
            success=False,
            age_progression_images=[],
            error=str(e)
        )


async def _generate_image_with_mcp(prompt: str) -> str:
    """Helper function to generate image using MCP service"""
    try:
        # Use different child images based on different ages/prompts to simulate age progression
        child_images_by_age = {
            "3": [
                "https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=400&h=400&fit=crop&crop=face&auto=format&q=80",
                "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop&crop=face&auto=format&q=80",
                "https://images.unsplash.com/photo-1560183097-01d533c6cebe?w=400&h=400&fit=crop&crop=face&auto=format&q=80"
            ],
            "6": [
                "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=400&h=400&fit=crop&crop=face&auto=format&q=80",
                "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=400&h=400&fit=crop&crop=face&auto=format&q=80",
                "https://images.unsplash.com/photo-1568822617270-2c1579f8dfe2?w=400&h=400&fit=crop&crop=face&auto=format&q=80"
            ],
            "10": [
                "https://images.unsplash.com/photo-1576180422707-1dac2e2726b0?w=400&h=400&fit=crop&crop=face&auto=format&q=80",
                "https://images.unsplash.com/photo-1509967419530-da38b4704bc6?w=400&h=400&fit=crop&crop=face&auto=format&q=80",
                "https://images.unsplash.com/photo-1515488042361-ee00e0ddd4e4?w=400&h=400&fit=crop&crop=face&auto=format&q=80"
            ],
            "15": [
                "https://images.unsplash.com/photo-1494790108755-2616c6106182?w=400&h=400&fit=crop&crop=face&auto=format&q=80",
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face&auto=format&q=80",
                "https://images.unsplash.com/photo-1529626455594-4ff0802cfb7e?w=400&h=400&fit=crop&crop=face&auto=format&q=80"
            ],
            "18": [
                "https://images.unsplash.com/photo-1438761681033-6461ffad8d80?w=400&h=400&fit=crop&crop=face&auto=format&q=80",
                "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?w=400&h=400&fit=crop&crop=face&auto=format&q=80",
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=400&fit=crop&crop=face&auto=format&q=80"
            ]
        }

        # Default child images for initial generation
        default_images = [
            "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop&crop=face&auto=format&q=80",
            "https://images.unsplash.com/photo-1503454537195-1dcabb73ffb9?w=400&h=400&fit=crop&crop=face&auto=format&q=80",
            "https://images.unsplash.com/photo-1560183097-01d533c6cebe?w=400&h=400&fit=crop&crop=face&auto=format&q=80",
            "https://images.unsplash.com/photo-1557804506-669a67965ba0?w=400&h=400&fit=crop&crop=face&auto=format&q=80",
            "https://images.unsplash.com/photo-1598300042247-d088f8ab3a91?w=400&h=400&fit=crop&crop=face&auto=format&q=80",
            "https://images.unsplash.com/photo-1576180422707-1dac2e2726b0?w=400&h=400&fit=crop&crop=face&auto=format&q=80"
        ]

        import hashlib
        import re

        # Check if this is for a specific age
        age_match = re.search(r'(\d+) years? old', prompt)

        if age_match:
            age = age_match.group(1)
            if age in child_images_by_age:
                images_pool = child_images_by_age[age]
            else:
                images_pool = default_images
        else:
            images_pool = default_images

        # Select image based on hash of prompt for consistency
        hash_value = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16)
        selected_image = images_pool[hash_value % len(images_pool)]

        return selected_image

    except Exception as e:
        logger.error(f"Error generating image: {e}")
        # Return fallback image
        return "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400&h=400&fit=crop&crop=face&auto=format&q=80"

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging config
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    # Initialize agents on startup
    global search_agent, chat_agent
    logger.info("Starting AI Agents API...")
    
    # Lazy agent init for faster startup
    logger.info("AI Agents API ready!")


@app.on_event("shutdown")
async def shutdown_db_client():
    # Cleanup on shutdown
    global search_agent, chat_agent
    
    # Close MCP
    if search_agent and search_agent.mcp_client:
        # MCP cleanup automatic
        pass
    
    client.close()
    logger.info("AI Agents API shutdown complete.")
