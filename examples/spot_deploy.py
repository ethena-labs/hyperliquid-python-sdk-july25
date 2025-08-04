# Example script to deploy HIP-1 and HIP-2 assets
# See https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/deploying-hip-1-and-hip-2-assets
# for the spec.
#
# IMPORTANT: Replace any arguments for the exchange calls below to match your deployment requirements.

import example_utils
from hyperliquid.utils import constants
from dotenv import load_dotenv, find_dotenv
from eth_account import Account
import os
env_path = find_dotenv()
load_dotenv(env_path)
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# deployer = Account.from_key(PRIVATE_KEY)
# deployer_address = deployer.address
# print(deployer_address)
deployer_address = "0x0d20d44Fbd48752241a2b18979dF2424e8a5F022"
#Note config.json also needs to be setup with deployer address pkey, in addition to having in env.

# Set to True to enable freeze functionality for the deployed token
# See step 2-a below for more details on freezing.
ENABLE_FREEZE_PRIVILEGE = True
# Set to True to set the deployer trading fee share
# See step 6 below for more details on setting the deployer trading fee share.
SET_DEPLOYER_TRADING_FEE_SHARE = False # Defaults to 100%, no need to set
DUMMY_USER = "0x0000000000000000000000000000000000000001"


def setup():
    pass

address, info, exchange = example_utils.setup(constants.TESTNET_API_URL, skip_ws=True)
initial_supply = 100_000_000_000 #100b
wei_decimals = 8
sz_decimals = 2
initial_supply_wei = initial_supply * 10 ** wei_decimals
max_gas = 260000000000 #Amount of HYPE to bid x 10**8
token = 1388 # Replace with value from step 1
def step1():

    # Step 1: Registering the Token
    #
    # Takes part in the spot deploy auction and if successful, registers token "TEST0"
    # with sz_decimals 2 and wei_decimals 8.
    # The max gas is 10,000 HYPE and represents the max amount to be paid for the spot deploy auction.
    register_token_result = exchange.spot_deploy_register_token("THUSDE", sz_decimals, wei_decimals, max_gas, "Test token THUSDE")
    print(register_token_result)
    # If registration is successful, a token index will be returned. This token index is required for
    # later steps in the spot deploy process.
    if register_token_result["status"] == "ok":
        token = register_token_result["response"]["data"]
    else:
        return


def step2():
    # Step 2: User Genesis
    user_genesis_result = exchange.spot_deploy_user_genesis(
        token,
        [
            (deployer_address.lower(), str(initial_supply_wei)),
        ],
        [],
    )
    print(user_genesis_result)

    if ENABLE_FREEZE_PRIVILEGE:
        # Step 2-a: Enables the deployer to freeze/unfreeze users. Freezing a user means
        # that user cannot trade, send, or receive this token.
        enable_freeze_privilege_result = exchange.spot_deploy_enable_freeze_privilege(token)
        print(enable_freeze_privilege_result)

        # # Freeze user for token
        # freeze_user_result = exchange.spot_deploy_freeze_user(token, DUMMY_USER, True)
        # print(freeze_user_result)
        #
        # # Unfreeze user for token
        # unfreeze_user_result = exchange.spot_deploy_freeze_user(token, DUMMY_USER, False)
        # print(unfreeze_user_result)

#
def step3():
    # Step 3: Genesis
    genesis_result = exchange.spot_deploy_genesis(token, str(initial_supply_wei), no_hyperliquidity=True)
    print(genesis_result)
#

def step4():
    # Step 4: Register Spot
    #
    # Register the spot pair (TEST0/USDC) given base and quote token indices. 0 represents USDC.
    # The base token is the first token in the pair and the quote token is the second token.
    register_spot_result = exchange.spot_deploy_register_spot(token, 0)
    print(register_spot_result)
    # If registration is successful, a spot index will be returned. This spot index is required for
    # registering hyperliquidity.
    if register_spot_result["status"] == "ok":
        spot = register_spot_result["response"]["data"]
    else:
        return

def step5():
    spot = 1258 #Change to value from step 4
    # Step 5: Register Hyperliquidity
    #
    # Registers hyperliquidity for the spot pair. In this example, hyperliquidity is registered
    # with a starting price of $2, an order size of 4, and 100 total orders.
    #
    # This step is required even if "noHyperliquidity" was set to True.
    # If "noHyperliquidity" was set to True during step 3 (genesis), then "n_orders" is required to be 0.
    register_hyperliquidity_result = exchange.spot_deploy_register_hyperliquidity(spot, 2.0, 4.0, 0, None)
    print(register_hyperliquidity_result)

    # if SET_DEPLOYER_TRADING_FEE_SHARE:
        # Step 6
        #
        # Note that the deployer trading fee share cannot increase.
        # The default is already 100% and the smallest increment is 0.001%.
        # set_deployer_trading_fee_share_result = exchange.spot_deploy_set_deployer_trading_fee_share(token, "100%")
        # print(set_deployer_trading_fee_share_result)


if __name__ == "__main__":
    step5()