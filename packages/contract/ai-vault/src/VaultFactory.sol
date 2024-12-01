// SPDX-License-Identifier: MIT
pragma solidity 0.8.24;

import "./BaseVault.sol";

contract VaultFactory {
    event VaultCreated(address indexed owner, address vaultAddress);

    mapping(address => address[]) public userVaults;

    function createVault(
        IERC20 asset,
        string memory name,
        string memory symbol
    ) external returns (address) {
        BaseVault vault = new BaseVault(asset, name, symbol);
        userVaults[msg.sender].push(address(vault));

        emit VaultCreated(msg.sender, address(vault));
        return address(vault);
    }

    function getVaults(address user) external view returns (address[] memory) {
        return userVaults[user];
    }
}
