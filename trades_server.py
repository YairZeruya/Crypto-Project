from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from app import app
from trade_manager import tradeManager

trade_manager = tradeManager()

@app.route('/trade/buy')
def buy():
    return 'Buy order placed'

@app.route('/trade/sell')
def sell():
    return 'Sell order placed'
