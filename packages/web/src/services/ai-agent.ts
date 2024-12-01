import axios from "axios";

const baseUrl = "http://localhost:8001";

export const createAgent = async (name: string, instructions: string) => {
    try {
        const response = await axios.post(baseUrl + "/create_agent", {
            name,
            instructions
        });

        return response.data;
    } catch (error) {
        console.error(error);
    }
}

export const createToken = async (agent_id: string, name: string, symbol: string, initial_supply: number) => {
    try {
        const response = await axios.post(baseUrl + "/create_token", {
            agent_id,
            name,
            symbol,
            initial_supply
        });

        return response.data;
    } catch (error) {
        console.error(error);
    }
}

