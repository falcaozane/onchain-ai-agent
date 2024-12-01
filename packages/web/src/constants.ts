import { defineChain } from 'viem';

const sourceId = 11_155_111

export const baseSepolia = defineChain({
  id: 84532,
  network: 'base-sepolia',
  name: 'Base Sepolia',
  nativeCurrency: { name: 'Sepolia Ether', symbol: 'ETH', decimals: 18 },
  rpcUrls: {
    default: {
      http: ['https://base-sepolia.blockscout.com/api/eth-rpc'],
    },
  },
  blockExplorers: {
    default: {
      name: 'Basescan',
      url: 'https://base-sepolia.blockscout.com',
      apiUrl: 'https://base-sepolia.blockscout.com/api',
    },
  },
  contracts: {
    disputeGameFactory: {
      [sourceId]: {
        address: '0xd6E6dBf4F7EA0ac412fD8b65ED297e64BB7a06E1',
      },
    },
    l2OutputOracle: {
      [sourceId]: {
        address: '0x84457ca9D0163FbC4bbfe4Dfbb20ba46e48DF254',
      },
    },
    portal: {
      [sourceId]: {
        address: '0x49f53e41452c74589e85ca1677426ba426459e85',
        blockCreated: 4446677,
      },
    },
    l1StandardBridge: {
      [sourceId]: {
        address: '0xfd0Bf71F60660E2f608ed56e1659C450eB113120',
        blockCreated: 4446677,
      },
    },
    multicall3: {
      address: '0xca11bde05977b3631167028862be2a173976ca11',
      blockCreated: 1059647,
    },
  },
  testnet: true,
  sourceId,
})


export const polygon = defineChain({
    id: 137,
    name: 'Polygon',
    nativeCurrency: { name: 'POL', symbol: 'POL', decimals: 18 },
    rpcUrls: {
      default: {
        http: ['https://polygon.blockscout.com/api/eth-rpc'],
      },
    },
    blockExplorers: {
      default: {
        name: 'PolygonScan',
        url: 'https://polygon.blockscout.com/',
        apiUrl: 'https://polygon.blockscout.com/api',
      },
    },
    contracts: {
      multicall3: {
        address: '0xca11bde05977b3631167028862be2a173976ca11',
        blockCreated: 25770160,
      },
    },
})
