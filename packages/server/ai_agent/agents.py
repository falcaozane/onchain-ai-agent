import json
from swarm import Agent
from cdp import *
from typing import List, Dict, Any
import os
from openai import OpenAI # type: ignore
from decimal import Decimal
from typing import Union
from web3 import Web3
from web3.exceptions import ContractLogicError
from cdp.errors import ApiError, UnsupportedAssetError
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from bson import ObjectId
from bson.errors import InvalidId
import time

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# MongoDB connection setup
MONGODB_URL = os.getenv("MONGODB_URL")
# Get configuration from environment variables
API_KEY_NAME = os.environ.get("CDP_API_KEY_NAME")
PRIVATE_KEY = os.environ.get("CDP_PRIVATE_KEY").replace('\\n', '\n')

# MongoDB connection setup
client = AsyncIOMotorClient(MONGODB_URL)
db = client.get_database("ai")
agent_collection = db.get_collection("agents")
# Configure CDP with environment variables
Cdp.configure(API_KEY_NAME, PRIVATE_KEY)

# Create a new wallet on the Base Sepolia testnet
# You could make this a function for the agent to create a wallet on any network
# If you want to use Base Mainnet, change Wallet.create() to Wallet.create(network_id="base-mainnet")
# see https://docs.cdp.coinbase.com/mpc-wallet/docs/wallets for more information

# NOTE: the wallet is not currently persisted, meaning that it will be deleted after the agent is stopped. To persist the wallet, see https://docs.cdp.coinbase.com/mpc-wallet/docs/wallets#developer-managed-wallets
# Here's an example of how to persist the wallet:
# WARNING: This is for development only - implement secure storage in production!

# # Export wallet data (contains seed and wallet ID)
# wallet_data = agent_wallet.export_data()
# wallet_dict = wallet_data.to_dict()

# # Example of saving to encrypted local file
# file_path = "wallet_seed.json"
# agent_wallet.save_seed(file_path, encrypt=True)
# print(f"Seed for wallet {agent_wallet.id} saved to {file_path}")

# # Example of loading a saved wallet:
# # 1. Fetch the wallet by ID
# fetched_wallet = Wallet.fetch(wallet_id)
# # 2. Load the saved seed
# fetched_wallet.load_seed("wallet_seed.json")

# Example of importing previously exported wallet data:
# imported_wallet = Wallet.import_data(wallet_dict)
# agent_wallet = Wallet.create()

# Request funds from the faucet (only works on testnet)
# faucet = agent_wallet.faucet()
# print(f"Faucet transaction: {faucet}")
# print(f"Agent wallet address: {agent_wallet.default_address.address_id}")

# Function to create and save an agent
async def create_agent(name: str, instructions: str) -> dict:
    """
    Create a new agent and save it in MongoDB.

    Args:
        name (str): The name of the agent.
        instructions (str): Instructions for the agent.

    Returns:
        dict: The agent data saved in MongoDB.
    """
    agent_wallet = Wallet.create()
    
    wallet_data = agent_wallet.export_data()
    wallet_dict = wallet_data.to_dict()
    # print(wallet_dict)

    # Request funds from the faucet (only works on testnet)
    # faucet = agent_wallet.faucet()
    # print(f"Faucet transaction: {faucet}")
    # print(f"Agent wallet address: {agent_wallet.default_address.address_id}")
    agent_data = {
        "name": name,
        "instructions": instructions,
        "wallet": agent_wallet.default_address.address_id
    }
    # Save to MongoDB
    result = await agent_collection.insert_one(agent_data)
    agent_data["_id"] = str(result.inserted_id)  # Convert ObjectId to string
    return agent_data



async def get_agent(agent_id: str) -> dict:
    """
    Retrieve agent details from the database.

    Args:
        agent_id (str): The ID of the agent.

    Returns:
        dict: The agent data, including wallet information.

    Raises:
        ValueError: If the agent ID is invalid or the agent is not found.
    """
    # Convert agent_id to ObjectId
    try:
        agent_id = ObjectId(agent_id)
    except InvalidId:
        raise ValueError("Invalid agent ID format.")

    # Retrieve agent data from MongoDB
    agent_data = await agent_collection.find_one({"_id": agent_id})
    if not agent_data:
        raise ValueError(f"Agent with ID {agent_id} not found.")

    return agent_data


# Function to create a new ERC-20 token
async def create_token(agent_id: str, name: str, symbol: str, initial_supply: int) -> str:
    """
    Create a new ERC-20 token.

    Args:
        agent_id (str): The ID of the agent.
        name (str): The name of the token.
        symbol (str): The symbol of the token.
        initial_supply (int): The initial supply of tokens.

    Returns:
        str: A message confirming the token creation with details.
    """
    # Get agent details
    agent_data = await get_agent(agent_id)

    wallet_data = agent_data.get("wallet")
    if not wallet_data:
        raise ValueError("Wallet data not found for the agent.")

    # Import the wallet
    agent_wallet = Wallet.import_data(WalletData(wallet_data.get("wallet_id"), wallet_data.get("seed")))

    # Deploy the ERC-20 token
    try:
        deployed_contract = agent_wallet.deploy_token(name, symbol, initial_supply)
        deployed_contract.wait()
    except Exception as e:
        raise RuntimeError(f"Failed to deploy token: {str(e)}")

    return (
        f"Token {name} ({symbol}) created with an initial supply of {initial_supply} "
        f"and contract address {deployed_contract.contract_address}."
    )

# Function to transfer assets
async def transfer_asset(agent_id, amount, asset_id, destination_address):
    """
    Transfer an asset to a specific address.
    
    Args:
        amount (Union[int, float, Decimal]): Amount to transfer
        asset_id (str): Asset identifier ("eth", "usdc") or contract address of an ERC-20 token
        destination_address (str): Recipient's address
    
    Returns:
        str: A message confirming the transfer or describing an error
    """
    try:
        # Get agent details
        agent_data = await get_agent(agent_id)

        wallet_data = agent_data.get("wallet")
        if not wallet_data:
            raise ValueError("Wallet data not found for the agent.")

        # Import the wallet
        agent_wallet = Wallet.import_data(WalletData(wallet_data.get("wallet_id"), wallet_data.get("seed")))
        # Check if we're on Base Mainnet and the asset is USDC for gasless transfer
        is_mainnet = agent_wallet.network_id == "base-mainnet"
        is_usdc = asset_id.lower() == "usdc"
        gasless = is_mainnet and is_usdc

        # For ETH and USDC, we can transfer directly without checking balance
        if asset_id.lower() in ["eth", "usdc"]:
            transfer = agent_wallet.transfer(amount,
                                             asset_id,
                                             destination_address,
                                             gasless=gasless)
            transfer.wait()
            gasless_msg = " (gasless)" if gasless else ""
            return f"Transferred {amount} {asset_id}{gasless_msg} to {destination_address}"

        # For other assets, check balance first
        try:
            balance = agent_wallet.balance(asset_id)
        except UnsupportedAssetError:
            return f"Error: The asset {asset_id} is not supported on this network. It may have been recently deployed. Please try again in about 30 minutes."

        if balance < amount:
            return f"Insufficient balance. You have {balance} {asset_id}, but tried to transfer {amount}."

        transfer = agent_wallet.transfer(amount, asset_id, destination_address)
        transfer.wait()
        return f"Transferred {amount} {asset_id} to {destination_address}"
    except Exception as e:
        return f"Error transferring asset: {str(e)}. If this is a custom token, it may have been recently deployed. Please try again in about 30 minutes, as it needs to be indexed by CDP first."


# Function to get the balance of a specific asset
async def get_balance(agent_id, asset_id):
    """
    Get the balance of a specific asset in the agent's wallet.
    
    Args:
        asset_id (str): Asset identifier ("eth", "usdc") or contract address of an ERC-20 token
    
    Returns:
        str: A message showing the current balance of the specified asset
    """
    # Get agent details
    agent_data = await get_agent(agent_id)

    wallet_data = agent_data.get("wallet")
    if not wallet_data:
        raise ValueError("Wallet data not found for the agent.")

    # Import the wallet
    agent_wallet = Wallet.import_data(WalletData(wallet_data.get("wallet_id"), wallet_data.get("seed")))
    balance = agent_wallet.balance(asset_id)
    return f"Current balance of {asset_id}: {balance}"


# Function to request ETH from the faucet (testnet only)
async def request_eth_from_faucet(agent_id):
    """
    Request ETH from the Base Sepolia testnet faucet.
    
    Returns:
        str: Status message about the faucet request
    """
    # Get agent details
    agent_data = await get_agent(agent_id)

    wallet_data = agent_data.get("wallet")
    if not wallet_data:
        raise ValueError("Wallet data not found for the agent.")

    # Import the wallet
    agent_wallet = Wallet.import_data(WalletData(wallet_data.get("wallet_id"), wallet_data.get("seed")))
    if agent_wallet.network_id == "base-mainnet":
        return "Error: The faucet is only available on Base Sepolia testnet."

    faucet_tx = agent_wallet.faucet()
    return f"Requested ETH from faucet. Transaction: {faucet_tx}"


# Function to generate art using DALL-E (requires separate OpenAI API key)
def generate_art(prompt):
    """
    Generate art using DALL-E based on a text prompt.
    
    Args:
        prompt (str): Text description of the desired artwork
    
    Returns:
        str: Status message about the art generation, including the image URL if successful
    """
    try:
        client = OpenAI()
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )

        image_url = response.data[0].url
        return f"Generated artwork available at: {image_url}"

    except Exception as e:
        return f"Error generating artwork: {str(e)}"


# Function to deploy an ERC-721 NFT contract
async def deploy_nft(agent_id, name, symbol, base_uri):
    """
    Deploy an ERC-721 NFT contract.
    
    Args:
        name (str): Name of the NFT collection
        symbol (str): Symbol of the NFT collection
        base_uri (str): Base URI for token metadata
    
    Returns:
        str: Status message about the NFT deployment, including the contract address
    """
    try:
        # Get agent details
        agent_data = await get_agent(agent_id)

        wallet_data = agent_data.get("wallet")
        if not wallet_data:
            raise ValueError("Wallet data not found for the agent.")

        # Import the wallet
        agent_wallet = Wallet.import_data(WalletData(wallet_data.get("wallet_id"), wallet_data.get("seed")))
        deployed_nft = agent_wallet.deploy_nft(name, symbol, base_uri)
        deployed_nft.wait()
        contract_address = deployed_nft.contract_address

        return f"Successfully deployed NFT contract '{name}' ({symbol}) at address {contract_address} with base URI: {base_uri}"

    except Exception as e:
        return f"Error deploying NFT contract: {str(e)}"


# Function to mint an NFT
async def mint_nft(agent_id, contract_address, mint_to):
    """
    Mint an NFT to a specified address.
    
    Args:
        contract_address (str): Address of the NFT contract
        mint_to (str): Address to mint NFT to
    
    Returns:
        str: Status message about the NFT minting
    """
    try:
        # Get agent details
        agent_data = await get_agent(agent_id)

        wallet_data = agent_data.get("wallet")
        if not wallet_data:
            raise ValueError("Wallet data not found for the agent.")

        # Import the wallet
        agent_wallet = Wallet.import_data(WalletData(wallet_data.get("wallet_id"), wallet_data.get("seed")))
        mint_args = {"to": mint_to, "quantity": "1"}

        mint_invocation = agent_wallet.invoke_contract(
            contract_address=contract_address, method="mint", args=mint_args)
        mint_invocation.wait()

        return f"Successfully minted NFT to {mint_to}"

    except Exception as e:
        return f"Error minting NFT: {str(e)}"


# Function to swap assets (only works on Base Mainnet)
async def swap_assets(agent_id: str, amount: Union[int, float, Decimal], from_asset_id: str,
                to_asset_id: str):
    """
    Swap one asset for another using the trade function.
    This function only works on Base Mainnet.

    Args:
        amount (Union[int, float, Decimal]): Amount of the source asset to swap
        from_asset_id (str): Source asset identifier
        to_asset_id (str): Destination asset identifier

    Returns:
        str: Status message about the swap
    """
    # Get agent details
    agent_data = await get_agent(agent_id)

    wallet_data = agent_data.get("wallet")
    if not wallet_data:
        raise ValueError("Wallet data not found for the agent.")

    # Import the wallet
    agent_wallet = Wallet.import_data(WalletData(wallet_data.get("wallet_id"), wallet_data.get("seed")))

    if agent_wallet.network_id != "base-mainnet":
        return "Error: Asset swaps are only available on Base Mainnet. Current network is not Base Mainnet."

    try:
        trade = agent_wallet.trade(amount, from_asset_id, to_asset_id)
        trade.wait()
        return f"Successfully swapped {amount} {from_asset_id} for {to_asset_id}"
    except Exception as e:
        return f"Error swapping assets: {str(e)}"


# Contract addresses for Basenames
BASENAMES_REGISTRAR_CONTROLLER_ADDRESS_MAINNET = "0x4cCb0BB02FCABA27e82a56646E81d8c5bC4119a5"
BASENAMES_REGISTRAR_CONTROLLER_ADDRESS_TESTNET = "0x49aE3cC2e3AA768B1e5654f5D3C6002144A59581"
L2_RESOLVER_ADDRESS_MAINNET = "0xC6d566A56A1aFf6508b41f6c90ff131615583BCD"
L2_RESOLVER_ADDRESS_TESTNET = "0x6533C94869D28fAA8dF77cc63f9e2b2D6Cf77eBA"
ENS_REGISTRAR_CONTROLLER_ADDRESS = ""


# Function to create registration arguments for Basenames
def create_register_contract_method_args(base_name: str, address_id: str,
                                         is_mainnet: bool) -> dict:
    """
    Create registration arguments for Basenames.
    
    Args:
        base_name (str): The Basename (e.g., "example.base.eth" or "example.basetest.eth")
        address_id (str): The Ethereum address
        is_mainnet (bool): True if on mainnet, False if on testnet
    
    Returns:
        dict: Formatted arguments for the register contract method
    """
    w3 = Web3()

    resolver_contract = w3.eth.contract(abi=l2_resolver_abi)

    name_hash = w3.ens.namehash(base_name)

    address_data = resolver_contract.encode_abi("setAddr",
                                                args=[name_hash, address_id])

    name_data = resolver_contract.encode_abi("setName",
                                             args=[name_hash, base_name])

    register_args = {
        "request": [
            base_name.replace(".base.eth" if is_mainnet else ".basetest.eth",
                              ""),
            address_id,
            "31557600",  # 1 year in seconds
            L2_RESOLVER_ADDRESS_MAINNET
            if is_mainnet else L2_RESOLVER_ADDRESS_TESTNET,
            [address_data, name_data],
            True
        ]
    }

    return register_args


# Function to register a basename
async def register_basename(agent_id: str, basename: str, amount: float = 0.002):
    """
    Register a basename for the agent's wallet.
    
    Args:
        basename (str): The basename to register (e.g. "myname.base.eth" or "myname.basetest.eth")
        amount (float): Amount of ETH to pay for registration (default 0.002)
    
    Returns:
        str: Status message about the basename registration
    """
    # Get agent details
    agent_data = await get_agent(agent_id)

    wallet_data = agent_data.get("wallet")
    if not wallet_data:
        raise ValueError("Wallet data not found for the agent.")

    # Import the wallet
    agent_wallet = Wallet.import_data(WalletData(wallet_data.get("wallet_id"), wallet_data.get("seed")))

    address_id = agent_wallet.default_address.address_id
    is_mainnet = agent_wallet.network_id == "base-mainnet"

    suffix = ".base.eth" if is_mainnet else ".basetest.eth"
    if not basename.endswith(suffix):
        basename += suffix

    register_args = create_register_contract_method_args(
        basename, address_id, is_mainnet)

    try:
        contract_address = (BASENAMES_REGISTRAR_CONTROLLER_ADDRESS_MAINNET
                            if is_mainnet else
                            BASENAMES_REGISTRAR_CONTROLLER_ADDRESS_TESTNET)

        invocation = agent_wallet.invoke_contract(
            contract_address=contract_address,
            method="register",
            args=register_args,
            abi=registrar_abi,
            amount=amount,
            asset_id="eth",
        )
        invocation.wait()
        return f"Successfully registered basename {basename} for address {address_id}"
    except ContractLogicError as e:
        return f"Error registering basename: {str(e)}"
    except Exception as e:
        return f"Unexpected error registering basename: {str(e)}"
    

def generate_commitment(name, owner, secret):
    return web3.solidityKeccak(
        ["string", "address", "bytes32"],
        [name, owner, secret]
)
    

async def register_ens_domain(agent_id:str, domain: str, owner: str, duration: int, secret: str, amount: float):
    """
    Register an ENS domain.

    Args:
        domain (str): The domain to register (e.g., "mydomain.eth")
        owner (str): Address of the owner.
        duration (int): Duration of the registration in seconds.
        secret (str): A secret for commitment.
        amount (float): Amount of ETH to pay for registration.

    Returns:
        str: Status message about the ENS domain registration.
    """
    COMMITMENT_WAIT_TIME = 60  # Minimum wait time in seconds
    try:
        commitment = generate_commitment(domain, owner, secret)

        # Get agent details
        agent_data = await get_agent(agent_id)

        wallet_data = agent_data.get("wallet")
        if not wallet_data:
            raise ValueError("Wallet data not found for the agent.")

        # Import the wallet
        agent_wallet = Wallet.import_data(WalletData(wallet_data.get("wallet_id"), wallet_data.get("seed")))

        # Commit step
        agent_wallet.invoke_contract(
            contract_address=ENS_REGISTRAR_CONTROLLER_ADDRESS,
            method="commit",
            args=[commitment],
            abi=commit_abi_ens,
        )

        # Wait for the commitment period (ENS-specific delay)
        time.sleep(COMMITMENT_WAIT_TIME)

        # Register step
        args = create_register_contract_method_args(domain, owner, duration, secret)
        invocation = agent_wallet.invoke_contract(
            contract_address=ENS_REGISTRAR_CONTROLLER_ADDRESS,
            method="register",
            args=args,
            abi=registrar_abi_ens,
            amount=amount,
            asset_id="eth",
        )
        invocation.wait()
        return f"Successfully registered domain {domain} for owner {owner}"
    except ContractLogicError as e:
        return f"Error registering ENS domain: {str(e)}"
    except Exception as e:
        return f"Unexpected error registering ENS domain: {str(e)}"

    

# Function to register a basename
async def interact_vault(agent_id: str, vault_address: str, action: str, amount: float, receiver: str):
    """
    Interact with a vault contract (deposit or withdraw).

    Args:
        agent_id (str): ID of the agent.
        vault_address (str): Address of the vault contract.
        action (str): The action to perform ('deposit' or 'withdraw').
        amount (float): Amount of assets (for deposit) or shares (for withdraw).
        receiver (str): Address of the receiver.

    Returns:
        str: Status message about the vault interaction.
    """
    # Get agent details
    agent_data = await get_agent(agent_id)

    wallet_data = agent_data.get("wallet")
    if not wallet_data:
        raise ValueError("Wallet data not found for the agent.")

    # Import the wallet
    agent_wallet = Wallet.import_data(WalletData(wallet_data.get("wallet_id"), wallet_data.get("seed")))

    try:
        if action == "deposit":
            # Prepare arguments for deposit
            vault_args = [amount, receiver]
            invocation = agent_wallet.invoke_contract(
                contract_address=vault_address,
                method="deposit",
                args=vault_args,
                abi=vault_abi,
            )
        elif action == "withdraw":
            # Prepare arguments for withdraw
            owner = agent_wallet.default_address.address_id
            vault_args = [amount, receiver, owner]
            invocation = agent_wallet.invoke_contract(
                contract_address=vault_address,
                method="withdraw",
                args=vault_args,
                abi=vault_abi,
            )
        else:
            return f"Invalid action '{action}'. Valid actions are 'deposit' or 'withdraw'."

        invocation.wait()
        return f"Successfully performed {action} of {amount} assets on the vault for receiver {receiver}."
    except ContractLogicError as e:
        return f"Error performing {action} on vault: {str(e)}"
    except Exception as e:
        return f"Unexpected error performing {action} on vault: {str(e)}"


# Create the Based Agent with all available functions
based_agent = Agent(
    name="Based Agent",
    instructions=
    "You are a helpful agent that can interact onchain on the Base Layer 2 using the Coinbase Developer Platform SDK. You can create tokens, transfer assets, generate art, deploy NFTs, mint NFTs, register basenames, and swap assets (on mainnet only). If you ever need to know your address, it is {agent_wallet.default_address.address_id}. If you ever need funds, you can request them from the faucet. You can also deploy your own ERC-20 tokens, NFTs, and interact with them. If someone asks you to do something you can't do, you can say so, and encourage them to implement it themselves using the CDP SDK, recommend they go to docs.cdp.coinbase.com for more informaton. You can also offer to help them implement it by writing the function and telling them to add it to the agents.py file and within your list of callable functions.",
    functions=[
        create_token,
        transfer_asset,
        get_balance,
        request_eth_from_faucet,
        #generate_art,  # Uncomment this line if you have configured the OpenAI API
        deploy_nft,
        mint_nft,
        swap_assets,
        register_basename,
        register_ens_domain,
        interact_vault
    ],
)

# ABIs for smart contracts (used in basename registration)
l2_resolver_abi = [{
    "inputs": [{
        "internalType": "bytes32",
        "name": "node",
        "type": "bytes32"
    }, {
        "internalType": "address",
        "name": "a",
        "type": "address"
    }],
    "name":
    "setAddr",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}, {
    "inputs": [{
        "internalType": "bytes32",
        "name": "node",
        "type": "bytes32"
    }, {
        "internalType": "string",
        "name": "newName",
        "type": "string"
    }],
    "name":
    "setName",
    "outputs": [],
    "stateMutability":
    "nonpayable",
    "type":
    "function"
}]

registrar_abi = [{
    "inputs": [{
        "components": [{
            "internalType": "string",
            "name": "name",
            "type": "string"
        }, {
            "internalType": "address",
            "name": "owner",
            "type": "address"
        }, {
            "internalType": "uint256",
            "name": "duration",
            "type": "uint256"
        }, {
            "internalType": "address",
            "name": "resolver",
            "type": "address"
        }, {
            "internalType": "bytes[]",
            "name": "data",
            "type": "bytes[]"
        }, {
            "internalType": "bool",
            "name": "reverseRecord",
            "type": "bool"
        }],
        "internalType":
        "struct RegistrarController.RegisterRequest",
        "name":
        "request",
        "type":
        "tuple"
    }],
    "name":
    "register",
    "outputs": [],
    "stateMutability":
    "payable",
    "type":
    "function"
}]

commit_abi_ens = [
    {
        "inputs": [
            { "internalType": "bytes32", "name": "commitment", "type": "bytes32" }
        ],
        "name": "commit",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

registrar_abi_ens = [
    {
        "inputs": [
            { "internalType": "string", "name": "name", "type": "string" },
            { "internalType": "address", "name": "owner", "type": "address" },
            { "internalType": "uint256", "name": "duration", "type": "uint256" },
            { "internalType": "bytes32", "name": "secret", "type": "bytes32" }
        ],
        "name": "register",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    }
]

vault_abi = [
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "assets",
                "type": "uint256"
            },
            {
                "internalType": "address",
                "name": "receiver",
                "type": "address"
            }
        ],
        "name": "deposit",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "shares",
                "type": "uint256"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "shares",
                "type": "uint256"
            },
            {
                "internalType": "address",
                "name": "receiver",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "owner",
                "type": "address"
            }
        ],
        "name": "withdraw",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "assets",
                "type": "uint256"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]