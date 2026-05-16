from flask import Flask, request, jsonify, render_template_string
import os
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

HTML = '''
<!DOCTYPE html>
<html>
<head>
    <title>OKX Trading Bot</title>
    <style>
        body { font-family: Arial; max-width: 600px; margin: 50px auto; padding: 20px; }
        .balance { background: #f0f0f0; padding: 20px; border-radius: 10px; margin: 20px 0; }
        .btn { padding: 15px 30px; font-size: 18px; margin: 10px; border: none; border-radius: 5px; cursor: pointer; }
        .buy { background: #28a745; color: white; }
        .sell { background: #dc3545; color: white; }
        .btn:disabled { opacity: 0.5; cursor: not-allowed; }
        .status { margin: 20px 0; padding: 10px; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; }
        .error { background: #f8d7da; color: #721c24; }
    </style>
</head>
<body>
    <h1>OKX Trading Bot</h1>
    <div class="balance">
        <h2>USDT 余额: <span id="balance">Loading...</span></h2>
        <button onclick="loadBalance()" style="padding:5px 10px;">Refresh</button>
    </div>
    
    <h3>Manual Trade</h3>
    <p>Symbol:</p>
    <select id="symbol" style="padding:10px;font-size:16px;">
        <option value="ETH/USDT">ETH/USDT</option>
        <option value="BTC/USDT">BTC/USDT</option>
        <option value="SOL/USDT">SOL/USDT</option>
        <option value="XRP/USDT">XRP/USDT</option>
        <option value="LINK/USDT">LINK/USDT</option>
        <option value="PEPE/USDT">PEPE/USDT</option>
    </select>
    
    <p>Amount:</p>
    <input type="number" id="amount" value="0.01" step="0.001" style="padding:10px;font-size:16px;">
    
    <div style="margin:20px 0;">
        <button class="btn buy" onclick="trade('buy')">BUY</button>
        <button class="btn sell" onclick="trade('sell')">SELL</button>
    </div>
    
    <div id="status"></div>
    
    <h3>How to use</h3>
    <ol>
        <li>Watch EMA9/EMA20 crossover on TradingView chart</li>
        <li>Golden cross (EMA9 crosses above EMA20) -> Click "BUY"</li>
        <li>Death cross (EMA9 crosses below EMA20) -> Click "SELL"</li>
    </ol>

    <script>
        async function loadBalance() {
            try {
                const res = await fetch('/test');
                const data = await res.json();
                document.getElementById('balance').textContent = data.USDT + ' USDT';
            } catch(e) {
                document.getElementById('balance').textContent = 'Load failed';
            }
        }
        
        async function trade(action) {
            const symbol = document.getElementById('symbol').value;
            const amount = parseFloat(document.getElementById('amount').value);
            
            const btn = document.querySelector('.' + action);
            btn.disabled = true;
            btn.textContent = 'Processing...';
            
            try {
                const res = await fetch('/' + action, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({symbol: symbol, amount: amount})
                });
                const data = await res.json();
                
                if (data.status === 'ok') {
                    document.getElementById('status').className = 'status success';
                    document.getElementById('status').textContent = action === 'buy' ? 'Buy success!' : 'Sell success!';
                } else {
                    document.getElementById('status').className = 'status error';
                    document.getElementById('status').textContent = 'Error: ' + data.error;
                }
            } catch(e) {
                document.getElementById('status').className = 'status error';
                document.getElementById('status').textContent = 'Network error';
            }
            
            btn.disabled = false;
            btn.textContent = action === 'buy' ? 'BUY' : 'SELL';
            loadBalance();
        }
        
        loadBalance();
    </script>
</body>
</html>
'''

@app.route('/')
def home():
    return render_template_string(HTML)

@app.route('/buy', methods=['POST'])
def buy():
    try:
        data = request.json
        symbol = data.get('symbol', 'ETH/USDT')
        amount = float(data.get('amount', 0.01))
        
        if symbol in SYMBOL_MAP:
            symbol = SYMBOL_MAP[symbol]
        
        order = okx.create_market_buy_order(symbol, amount)
        return jsonify({'status': 'ok', 'order': order})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/sell', methods=['POST'])
def sell():
    try:
        data = request.json
        symbol = data.get('symbol', 'ETH/USDT')
        amount = float(data.get('amount', 0.01))
        
        if symbol in SYMBOL_MAP:
            symbol = SYMBOL_MAP[symbol]
        
        order = okx.create_market_sell_order(symbol, amount)
        return jsonify({'status': 'ok', 'order': order})
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
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)