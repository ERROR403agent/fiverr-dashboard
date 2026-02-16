#!/usr/bin/env python3
"""
EXEC Trading Dashboard - Live Data API
Fetches wallet data from Base chain via RPC
"""
from flask import Flask, jsonify
from web3 import Web3
import json
from datetime import datetime

app = Flask(__name__)

# Base mainnet RPC
w3 = Web3(Web3.HTTPProvider('https://mainnet.base.org'))

# EXEC wallet
WALLET = Web3.to_checksum_address('0x47ffc880cfF2e8F18fD9567faB5a1fBD217B5552')

# Token contracts
USDC = Web3.to_checksum_address('0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913')
WETH = Web3.to_checksum_address('0x4200000000000000000000000000000000000006')
AERO = Web3.to_checksum_address('0x940181a94a35a4569e4529a3cdfb74e38fd98631')

# ERC20 ABI (balanceOf)
ERC20_ABI = json.loads('[{"inputs":[{"internalType":"address","name":"account","type":"address"}],"name":"balanceOf","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"}]')

ETH_PRICE = 1943.16  # Could fetch from price oracle in production

@app.route('/api/position')
def get_position():
    """Get current wallet position"""
    try:
        # Get native ETH
        eth_balance = w3.eth.get_balance(WALLET)
        eth_amount = float(w3.from_wei(eth_balance, 'ether'))
        
        # Get WETH
        weth_contract = w3.eth.contract(address=WETH, abi=ERC20_ABI)
        weth_balance = weth_contract.functions.balanceOf(WALLET).call()
        weth_amount = float(w3.from_wei(weth_balance, 'ether'))
        
        # Get USDC
        usdc_contract = w3.eth.contract(address=USDC, abi=ERC20_ABI)
        usdc_balance = usdc_contract.functions.balanceOf(WALLET).call()
        usdc_amount = usdc_balance / 1e6
        
        # Get AERO
        aero_contract = w3.eth.contract(address=AERO, abi=ERC20_ABI)
        aero_balance = aero_contract.functions.balanceOf(WALLET).call()
        aero_amount = float(w3.from_wei(aero_balance, 'ether'))
        
        # Calculate values
        eth_value = eth_amount * ETH_PRICE
        weth_value = weth_amount * ETH_PRICE
        usdc_value = usdc_amount
        aero_value = aero_amount * 0.30  # AERO ~$0.30
        
        total_value = eth_value + weth_value + usdc_value + aero_value
        
        # Calculate tradeable (excluding gas reserve)
        gas_reserve = 0.002
        tradeable_eth = max(0, eth_amount - gas_reserve)
        total_tradeable = (tradeable_eth * ETH_PRICE) + weth_value + usdc_value + aero_value
        
        # P&L calculation
        starting_capital = 74.12  # Starting value
        pnl = total_value - starting_capital
        pnl_percent = (pnl / starting_capital) * 100
        
        return jsonify({
            'success': True,
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'position': {
                'eth': {
                    'amount': eth_amount,
                    'value': eth_value
                },
                'weth': {
                    'amount': weth_amount,
                    'value': weth_value
                },
                'usdc': {
                    'amount': usdc_amount,
                    'value': usdc_value
                },
                'aero': {
                    'amount': aero_amount,
                    'value': aero_value
                }
            },
            'total': {
                'value': total_value,
                'tradeable': total_tradeable,
                'gas_reserve': gas_reserve * ETH_PRICE
            },
            'pnl': {
                'amount': pnl,
                'percent': pnl_percent,
                'starting_capital': starting_capital
            },
            'prices': {
                'eth': ETH_PRICE,
                'aero': 0.30
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/trades')
def get_trades():
    """Get trade history"""
    # Hardcoded for now - could fetch from Basescan API
    trades = [
        {
            'id': 1,
            'type': 'ETH → USDC',
            'amount_in': '0.014457 ETH',
            'amount_out': '27.92 USDC',
            'value': 28.09,
            'timestamp': '2026-02-15T20:02:00Z',
            'tx_hash': '0x20cbb01f9c6ed3d8dd3c18e5904de24e6113bdecb129fdc6ccc5cbc5367f434f',
            'platform': 'BaseSwap',
            'reasoning': 'Pivoted from AERO (routing issues). Swapped to USDC for liquidity.'
        },
        {
            'id': 2,
            'type': 'USDC → WETH',
            'amount_in': '27.92 USDC',
            'amount_out': '0.014182 WETH',
            'value': 27.56,
            'timestamp': '2026-02-16T04:02:00Z',
            'tx_hash': '0xb6065d2e865eaa974e2a753530b0793fb08f0f16f841ea080e5475f8739de125',
            'platform': 'BaseSwap',
            'reasoning': 'Active trading mode. Deployed 100% of USDC holdings.'
        }
    ]
    
    return jsonify({
        'success': True,
        'trades': trades,
        'total_trades': len(trades)
    })

@app.route('/api/stats')
def get_stats():
    """Get trading statistics"""
    return jsonify({
        'success': True,
        'stats': {
            'total_trades': 2,
            'trades_today': 2,
            'win_rate': 0,  # Too early to calculate
            'avg_hold_time': '8 hours',
            'gas_spent': 0.0013,
            'days_active': 1
        }
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=False)
