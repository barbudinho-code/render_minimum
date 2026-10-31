#!/usr/bin/env python3
"""Aplicação Hello World Flask para Render."""
from flask import Flask, render_template_string

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/greeting')
def greeting():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Hello, World!</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            text-align: center;
            padding: 50px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }
        h1 {
            font-size: 3rem;
            margin-bottom: 20px;
        }
        p {
            font-size: 1.5rem;
            opacity: 0.9;
        }
    </style>
</head>
<body>
    <h1>🎉 Hello, World! 🎉</h1>
    <p>Bem-vindo à sua aplicação Render!</p>
</body>
</html>'''

@app.route('/status')
def status():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Status - Hello World</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 600px;
            margin: 50px auto;
            padding: 20px;
            background: #f5f5f5;
        }
        .status-box {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }
        h2 { color: #333; }
        .success { color: green; }
    </style>
</head>
<body>
    <div class="status-box">
        <h2>✅ Application Status: Healthy</h2>
        <p><strong>Name:</strong> hello-world-app</p>
        <p><strong>Platform:</strong> Render (Git deployment)</p>
        <p><strong>Region:</strong> US</p>
        <p><strong>Language:</strong> Python / Flask</p>
    </div>
</body>
</html>'''

@app.route('/ws')
def websocket():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>WebSocket - Hello World</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px; }
        textarea { width: 100%; height: 200px; margin: 10px 0; font-size: 14px; }
    </style>
</head>
<body>
    <h2>Test de WebSocket</h2>
    <p>Simulação simples usando Ajax (sem WebSocket real):</p>
    <textarea id="output" readonly></textarea>
    <button onclick="sendGreeting()">Enviar Saudação</button>
    <script>
        function sendGreeting() {
            const output = document.getElementById('output');
            output.value = 'Hello, World!\\n';
            setTimeout(() => output.value += 'Bem-vindo à sua aplicação!', 500);
        }
        // Ao carregar, mostra mensagem inicial
        sendGreeting();
    </script>
</body>
</html>'''

if __name__ == '__main__':
    app.run(port=5000)
