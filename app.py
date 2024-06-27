from datetime import datetime
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from binance.client import Client
from app_manager import AppManager
import logging

app = Flask(__name__)
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app_manager = AppManager('trades.db')

@app.route('/binance')
@cross_origin()
def get_coins_binance():
    try:
        coins = app_manager.get_coins_binance()
        return jsonify(coins)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/binance/<coin>')
def get_coin_data(coin):
    try:
        timeframe = request.args.get('timeframe', default='1d')
        data = app_manager.get_coin_data(coin, timeframe)
        return jsonify(data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/strategy_descriptions')
def get_strategy_descriptions():
    try:
        descriptions = app_manager.get_strategy_descriptions()
        return jsonify(descriptions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/strategies')
def get_strategies():
    try:
        strategies = app_manager.get_strategies()
        return jsonify(strategies)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/backtest/<strategy_name>')
def run_backtest_all(strategy_name):
    try:
        timeframe = request.args.get('timeframe', default='1h')
        interval = int(request.args.get('interval', default=30))

        results = app_manager.run_backtest_all(strategy_name, timeframe, interval)
        return jsonify(results)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
        
@app.route('/trade/buy', methods=['POST'])
def buy():
    try:
        data = request.json
        symbol = data['symbol']
        cost = int(data['cost'])
        start_time = data['start_time']
        bot_name = data['bot_name']

        if not all([symbol, cost, start_time, bot_name]):
            raise ValueError("Missing required data")

        new_trade = app_manager.create_trade(symbol, cost, start_time, bot_name)
        return jsonify(new_trade.to_dict()), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# @app.route('/trade/<int:trade_id>', methods=['GET', 'PUT'])
# def get_trade_by_id(trade_id):
#     if request.method == 'GET':
#         trade = app_manager.get_trade_by_id(trade_id)
#         if trade:
#             return jsonify(trade.to_dict()), 200
#         else:
#             return jsonify({"error": f"Trade with ID {trade_id} not found"}), 404
        
    
@app.route('/trade/<int:trade_id>', methods=['GET', 'PUT'])
def get_trade_by_id(trade_id):
    if request.method == 'GET':
        try:
            trade = app_manager.get_trade_by_id(trade_id)
            if trade:
                response = jsonify(trade)
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                return response, 200
            else:
                return jsonify({"error": f"Trade with ID {trade_id} not found"}), 404
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    elif request.method == 'PUT':
        try:
            print(f"Received request to update trade ID {trade_id}")
            data = request.json
            print(f"Request data: {data}")
            end_time = data.get('end_time', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            print(f"End time: {end_time}")
            updated_trade = app_manager.sell_trade(trade_id, end_time)
            print(f"Updated trade: {updated_trade.to_dict()}")
            return jsonify(updated_trade.to_dict()), 200
        except ValueError as ve:
            return jsonify({"error": str(ve)}), 404  # Adjust status code as needed
        except Exception as e:
            logging.error(f"An error occurred in update trade endpoint: {str(e)}")
            return jsonify({"error": str(e)}), 500
    
@app.route('/trade/status/<int:trade_id>', methods=['GET'])
@cross_origin()
def sell_trade(trade_id):
    try:
        end_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        updated_trade = app_manager.sell_trade(trade_id, end_time)
        return jsonify(updated_trade.to_dict()), 200
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 404  # Adjust status code as needed
    except Exception as e:
        logging.error(f"An error occurred in sell_trade endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500
    
@app.route('/trades', methods=['GET'])
def get_all_trades():
    try:
        trades = app_manager.get_all_trades()
        return jsonify([trade for trade in trades]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/')
def hello():
    return 'Hello, World!'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5586, debug=True)
