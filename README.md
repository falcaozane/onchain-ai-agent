# Onchain AI Agent Platform

### Project Structures
1. packages/web \
1.1 Interface to create Vault and Agent
2. packages/contract/ai-vault \
2.1 Vault Contract
3. package/server \
3.1 Fast API + AI Agent with CDP and LLM

### How to run
1. web \
1.1 pnpm i \
1.2 pnpm dev
2. contract/ai-vault \
1.1 forge install \
1.2 cp .env.example .env and replace with your private key \
1.3 forge script script/Deploy.s.sol:Deploy --rpc-url https://sepolia.base.org --broadcast \
1.4 forge script script/Deploy.s.sol:Deploy --rpc-url https://rpc-amoy.polygon.technology --broadcast
3. server \
1.1 cp .env.example .env and replace with your config \
1.2 export OPENAI_API_KEY=<YOUR_OPENAI_KEY> \
1.3 poetry install \
1.4 poetry run uvicorn ai_agent.server:app --reload --host 0.0.0.0 --port 8001

### Note
- Now, AI platfrom is not fully intgrated Frontend, Backend, and Smart Contract, cause of time limit, you can test it seperately for CDP & LLM can run&test via Backend(API), for FE side now can create USDC Vault and AI agent with API

### Screenshots:
![SS1](/3.png "ss1")
![SS2](/1.png "ss2")
![SS3](/2.png "ss3")
![SS4](/4.png "ss4")