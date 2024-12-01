// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/extensions/ERC4626.sol";
import "@openzeppelin/contracts/token/ERC20/IERC20.sol";

contract BaseVault is ERC4626 {
    // Mapping to store fund managers for each user
    mapping(address => address) private fundManagers;

    // Events
    event FundManagerAssigned(address indexed user, address indexed fundManager);
    event FundManagerRevoked(address indexed user, address indexed fundManager);

    constructor(IERC20 asset, string memory name, string memory symbol)
        ERC4626(asset)
        ERC20(name, symbol)
    {}

    // Modifier to allow only the user or their fund manager to act
    modifier onlyUserOrFundManager(address user) {
        require(
            msg.sender == user || msg.sender == fundManagers[user],
            "Not authorized"
        );
        _;
    }

    // Function to assign a fund manager
    function assignFundManager(address manager) external {
        require(manager != address(0), "Invalid address");
        fundManagers[msg.sender] = manager;

        emit FundManagerAssigned(msg.sender, manager);
    }

    // Function to revoke a fund manager
    function revokeFundManager() external {
        address currentManager = fundManagers[msg.sender];
        require(currentManager != address(0), "No fund manager assigned");

        fundManagers[msg.sender] = address(0);

        emit FundManagerRevoked(msg.sender, currentManager);
    }

    // Function to get the fund manager for a user
    function getFundManager(address user) external view returns (address) {
        return fundManagers[user];
    }

    // Overridden deposit function to allow fund manager access
    function deposit(
        uint256 assets,
        address receiver
    ) public override onlyUserOrFundManager(receiver) returns (uint256 shares) {
        return super.deposit(assets, receiver);
    }

    // Overridden withdraw function to allow fund manager access
    function withdraw(
        uint256 assets,
        address receiver,
        address owner
    ) public override onlyUserOrFundManager(owner) returns (uint256 shares) {
        return super.withdraw(assets, receiver, owner);
    }
}
