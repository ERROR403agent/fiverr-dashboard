#!/usr/bin/env python3
"""
EXEC Trading Dashboard API
Real-time wallet monitoring, trade history, P&L tracking
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import json
import time
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
BASESCAN_API_KEY = "JMN38XVG9CUIPKDGWF7EYZD7J99VVY874C"
EXEC_WALLET = "0x47ffc880cfF2e8F18fD9567faB5a1fBD217B5552"
BASE_CHAIN_ID = 8453
STARTING_CAPITAL_USD = 114.00  # Original capital
ETH_STARTING_PRICE = 3000  # Will be updated

# Cache to avoid API rate limits
cache = {
    'balance': {'data': None, 'timestamp': 0, 'ttl': 30},
    'txlist': {'data': None, 'timestamp': 0, 'ttl': 60},
    'eth_price': {'data': None, 'timestamp': 0, 'ttl': 300}
}

def get_cached(key):
    """Get cached data if still valid"""
    if cache[key]['data'] and time.time() - cache[key]['timestamp'] < cache[key]['ttl']:
        return cache[key]['data']
    return None

def set_cache(key, data):
    """Set cache with timestamp"""
    cache[key]['data'] = data
    cache[key]['timestamp'] = time.time()

@app.route('/api/wallet', methods=['GET'])
def get_wallet():
    """Get current wallet balance (ETH + tokens)"""
    cached = get_cached('balance')
    if cached:
        return jsonify(cached)
    
    try:
        # Get ETH balance (using simple endpoint, no v2 issues)
        response = requests.get(
            f"https://api.basescan.org/api",
            params={
                'module': 'account',
                'action': 'balance',
                'address': EXEC_WALLET,
                'tag': 'latest',
                'apikey': BASESCAN_API_KEY
            },
            timeout=10
        )
        
        data = response.json()
        
        if data['status'] == '1':
            wei_balance = int(data['result'])
            eth_balance = wei_balance / 1e18
            
            # Get ETH price
            eth_price = get_eth_price()
            usd_value = eth_balance * eth_price
            
            result = {
                'address': EXEC_WALLET,
                'eth_balance': eth_balance,
                'eth_price': eth_price,
                'usd_value': usd_value,
                'timestamp': int(time.time()),
                'chain': 'Base',
                'chain_id': BASE_CHAIN_ID
            }
            
            set_cache('balance', result)
            return jsonify(result)
        else:
            return jsonify({'error': data.get('message', 'API error'), 'status': 'error'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/trades', methods=['GET'])
def get_trades():
    """Get transaction history and parse trades"""
    cached = get_cached('txlist')
    if cached:
        return jsonify(cached)
    
    try:
        # Get normal transactions
        response = requests.get(
            f"https://api.basescan.org/api",
            params={
                'module': 'account',
                'action': 'txlist',
                'address': EXEC_WALLET,
                'startblock': 0,
                'endblock': 99999999,
                'page': 1,
                'offset': 100,
                'sort': 'desc',
                'apikey': BASESCAN_API_KEY
            },
            timeout=10
        )
        
        data = response.json()
        
        if data['status'] == '1':
            transactions = data['result']
            
            # Parse into trades
            trades = []
            for tx in transactions:
                trade = {
                    'hash': tx['hash'],
                    'timestamp': int(tx['timeStamp']),
                    'date': datetime.fromtimestamp(int(tx['timeStamp'])).strftime('%Y-%m-%d %H:%M:%S'),
                    'from': tx['from'],
                    'to': tx['to'],
                    'value_eth': float(tx['value']) / 1e18,
                    'gas_used': int(tx['gasUsed']),
                    'gas_price_gwei': float(tx['gasPrice']) / 1e9,
                    'success': tx['isError'] == '0',
                    'block': int(tx['blockNumber'])
                }
                
                # Calculate gas cost in ETH
                trade['gas_cost_eth'] = (trade['gas_used'] * float(tx['gasPrice'])) / 1e18
                
                # Classify transaction type
                if tx['from'].lower() == EXEC_WALLET.lower():
                    trade['type'] = 'outgoing'
                elif tx['to'].lower() == EXEC_WALLET.lower():
                    trade['type'] = 'incoming'
                else:
                    trade['type'] = 'contract'
                
                trades.append(trade)
            
            result = {
                'trades': trades,
                'count': len(trades),
                'timestamp': int(time.time())
            }
            
            set_cache('txlist', result)
            return jsonify(result)
        else:
            return jsonify({'error': data.get('message', 'API error'), 'status': 'error'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/pnl', methods=['GET'])
def get_pnl():
    """Calculate profit/loss from starting capital"""
    try:
        wallet_data = get_wallet().json
        if 'error' in wallet_data:
            return jsonify(wallet_data), 500
        
        current_usd = wallet_data['usd_value']
        pnl_usd = current_usd - STARTING_CAPITAL_USD
        pnl_percent = (pnl_usd / STARTING_CAPITAL_USD) * 100
        
        result = {
            'starting_capital_usd': STARTING_CAPITAL_USD,
            'current_value_usd': current_usd,
            'pnl_usd': pnl_usd,
            'pnl_percent': pnl_percent,
            'timestamp': int(time.time())
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/comments', methods=['GET', 'POST'])
def handle_comments():
    """Store and retrieve dashboard comments"""
    COMMENTS_FILE = 'exec_comments.json'
    
    if request.method == 'GET':
        try:
            if os.path.exists(COMMENTS_FILE):
                with open(COMMENTS_FILE, 'r') as f:
                    comments = json.load(f)
            else:
                comments = []
            
            return jsonify({'comments': comments, 'count': len(comments)})
        except Exception as e:
            return jsonify({'error': str(e), 'status': 'error'}), 500
    
    elif request.method == 'POST':
        try:
            data = request.json
            author = data.get('author', 'Anonymous')
            content = data.get('content', '')
            
            # Basic prompt injection protection
            forbidden_patterns = [
                'ignore', 'disregard', 'forget', 'system:', 'assistant:',
                'prompt:', '<script>', 'javascript:', 'eval('
            ]
            
            content_lower = content.lower()
            for pattern in forbidden_patterns:
                if pattern in content_lower:
                    return jsonify({'error': 'Invalid content', 'status': 'error'}), 400
            
            # Load existing comments
            if os.path.exists(COMMENTS_FILE):
                with open(COMMENTS_FILE, 'r') as f:
                    comments = json.load(f)
            else:
                comments = []
            
            # Add new comment
            comment = {
                'id': len(comments) + 1,
                'author': author[:50],  # Limit author name length
                'content': content[:500],  # Limit content length
                'timestamp': int(time.time()),
                'date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            comments.append(comment)
            
            # Save
            with open(COMMENTS_FILE, 'w') as f:
                json.dump(comments, f, indent=2)
            
            return jsonify({'status': 'success', 'comment': comment})
            
        except Exception as e:
            return jsonify({'error': str(e), 'status': 'error'}), 500

def get_eth_price():
    """Get current ETH price in USD"""
    cached = get_cached('eth_price')
    if cached:
        return cached
    
    try:
        # Use CoinGecko free API
        response = requests.get(
            'https://api.coingecko.com/api/v3/simple/price',
            params={'ids': 'ethereum', 'vs_currencies': 'usd'},
            timeout=5
        )
        data = response.json()
        price = data['ethereum']['usd']
        
        set_cache('eth_price', price)
        return price
    except:
        # Fallback to approximate price
        return 3000.0

@app.route('/api/status', methods=['GET'])
def status():
    """Health check"""
    return jsonify({
        'status': 'online',
        'wallet': EXEC_WALLET,
        'chain': 'Base',
        'timestamp': int(time.time())
    })

if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=5002, debug=True)
