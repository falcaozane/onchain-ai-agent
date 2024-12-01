// SPDX-License-Identifier: MIT
pragma solidity >=0.8.24;

import {Script, console} from "forge-std/Script.sol";
import {IERC20} from "openzeppelin-contracts/contracts/token/ERC20/IERC20.sol";

import "../src/VaultFactory.sol";

contract Deploy is Script {
  function run() external {
    // Load the private key from the `PRIVATE_KEY` environment variable (in .env)
    uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
    // Start broadcasting transactions from the deployer account
    vm.startBroadcast(deployerPrivateKey);

    // Deploy the VaultFactory contract
    VaultFactory vaultFactory = new VaultFactory();
    // Print the address of the deployed contract
    console.log("VaultFactory deployed at: ", address(vaultFactory));

    vm.stopBroadcast();
  }
}