from flask import Flask, request, jsonify
import ccxt

app = Flask(__name__)

API_KEY = "03ab02d5-53b5-4af8-af42-a9e1f1ab8baa"
API_SECRET = "B0FE154C3293A0C46F2AB1FA555CFBCE"
PASSPHRASE = "Aa778778@"

okx = ccxt.okx({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'password': PASSPHRASE,
    'enableRateLimit': True,
})

SYMBOL_MAP = {
    'BTC': 'BTC/USDT',
    'ETH': 'ETH/USDT',
    'SOL': 'SOL/USDT',
    'XRP': 'XRP/USDT',
    'LINK': 'LINK/USDT',
    'PEPE': 'PEPE/USDT',
}

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json
        action = data.get('action', '').lower()
        symbol = data.get('symbol', 'ETH/USDT')
        amount = float(data.get('amount', 0.01))
        
        if symbol in SYMBOL_MAP:
            symbol = SYMBOL_MAP[symbol]
        
        if action == 'buy':
            order = okx.create_market_buy_order(symbol, amount)
            return jsonify({'status': 'ok', 'order': order})
        elif action == 'sell':
            order = okx.create_market_sell_order(symbol, amount)
            return jsonify({'status': 'ok', 'order': order})
        else:
            return jsonify({'error': 'Unknown action'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/test')
def test():
    try:
        bal = okx.fetch_balance()
        usdt = bal.get('total', {}).get('USDT', 0)
        return jsonify({'status': 'ok', 'USDT': usdt})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)