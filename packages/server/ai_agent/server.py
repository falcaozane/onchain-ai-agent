from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai_agent.agents import create_token, transfer_asset, get_balance, deploy_nft, mint_nft, create_agent

# Initialize FastAPI app
app = FastAPI()

# Define the allowed origins
origins = [
    "http://localhost:5173",
    "http://localhost:3000",  # Example: frontend running on localhost
    "https://yourdomain.com",  # Replace with your domain
]

# Add CORSMiddleware to your FastAPI app
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific origins
    allow_credentials=True,  # Allow credentials (cookies, Authorization headers, etc.)
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all HTTP headers
)

@app.get("/")
def read_root():
    return {"message": "Welcome to Based Agent API"}

# --- API Models ---
class TransferRequest(BaseModel):
    amount: float
    asset_id: str
    destination_address: str

class NFTRequest(BaseModel):
    name: str
    symbol: str
    base_uri: str

class MintRequest(BaseModel):
    contract_address: str
    mint_to: str

class AgentRequest(BaseModel):
    name: str
    instructions: str

class CreateTokenRequest(BaseModel):
    agent_id: str
    name: str
    symbol: str
    initial_supply: int

# --- API Endpoints ---
@app.post("/create_token")
async def api_create_token(request: CreateTokenRequest):
    try:
        result = await create_token(
            agent_id=request.agent_id,
            name=request.name,
            symbol=request.symbol,
            initial_supply=request.initial_supply,
        )
        return {"message": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.post("/transfer_asset")
def api_transfer_asset(request: TransferRequest):
    try:
        result = transfer_asset(request.amount, request.asset_id, request.destination_address)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/balance/{asset_id}")
def api_get_balance(asset_id: str):
    try:
        result = get_balance(asset_id)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/deploy_nft")
def api_deploy_nft(request: NFTRequest):
    try:
        result = deploy_nft(request.name, request.symbol, request.base_uri)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/mint_nft")
def api_mint_nft(request: MintRequest):
    try:
        result = mint_nft(request.contract_address, request.mint_to)
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/create_agent")
async def api_create_agent(request: AgentRequest):
    """
    Endpoint to create a new agent and save it in MongoDB.
    """
    try:
        agent_data = await create_agent(request.name, request.instructions)
        # Return the agent data as JSON-serializable format
        return {
            "message": "Agent created successfully.",
            "agent": agent_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
