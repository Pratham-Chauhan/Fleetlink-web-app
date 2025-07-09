# app.py
from datetime import datetime
from flask import Flask, render_template, render_template_string, request, jsonify
from threading import Thread
from multiprocessing import Process

from atu_scraper import ATUScraper
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string('''<!DOCTYPE html>
<html>

<head>
  <meta charset="UTF-8" />
  <title>Start Scraper</title>
  <style>
    body {
      font-family: Arial, sans-serif;
      padding: 40px;
      background: #f5f7fa;
    }

    .container {
      max-width: 800px;
      margin: auto;
      background: #fff;
      padding: 30px;
      border-radius: 10px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
    }

    textarea {
      width: 100%;
      height: 400px;
      font-family: monospace;
      font-size: 14px;
      padding: 10px;
      border: 1px solid #ccc;
      border-radius: 6px;
    }

    button {
      padding: 12px 24px;
      font-size: 16px;
      margin-top: 10px;
      background: #007bff;
      color: white;
      border: none;
      border-radius: 6px;
      cursor: pointer;
    }

    button:hover {
      background: #0056b3;
    }

    #responseBox {
      margin-top: 20px;
      background: #f0f0f0;
      padding: 15px;
      border-radius: 6px;
      font-family: monospace;
      white-space: pre-wrap;
    }
  </style>
</head>

<body>
  <div class="container">
    <h2>🧪 Test Your Scraper</h2>
    <p>Edit or paste your test JSON data below:</p>

    <textarea id="jsonInput">
{
  "pin_code": "64347",
  "id_target": [26],
  "target_service_group": [],
  "service_name": [],
  "target_manufacturer": "FORD",
  "target_model": "KA",
  "target_year": "2011",
  "quantity_amount": "1",
  "target_date": "12.06.2025",
  "engine": "electric",
  "your_data": {
    "firstName": "Dominik",
    "lastName": "Skakuj",
    "email": "dominik.skakuj1234@gmail.com",
    "mobile": "11111111111",
    "Erreichbarkeit": "",
    "licensePlate": "Da HI 2001",
    "HSN": "",
    "TSN": "",
    "mileage": "",
    "Radeinlagerungsnummer": "",
    "Firmenname": "",
    "Kundennummer": "",
    "Anmerkung": ""
  }
}</textarea>

  <p>Select Browser Type:</p>
  <div>
    <label><input type="radio" name="browser" value="Opera" checked> Opera</label><br>
    <label><input type="radio" name="browser" value="Camoufox"> Camoufox</label><br>
  </div>


    <button onclick="startScraper()">🚀 Start Scraper</button>

    <div id="responseBox"></div>
  </div>

  <script>
    async function startScraper() {
      const responseBox = document.getElementById("responseBox");
      const jsonData = document.getElementById("jsonInput").value;
      
      const browserType = document.querySelector('input[name="browser"]:checked').value;

      try {
        const parsed = JSON.parse(jsonData);
        responseBox.textContent = "⏳ Sending data...";

        const res = await fetch(`/run-scraper?browser_type=${encodeURIComponent(browserType)}`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(parsed),
        });

        const result = await res.json();
        responseBox.textContent = JSON.stringify(result, null, 2);
      } catch (err) {
        responseBox.textContent = "❌ Invalid JSON or error: " + err.message;
      }
    }
  </script>
</body>

</html>
''')

@app.route('/run-scraper', methods=['POST'])
def webhook():
    data = request.get_json()
    browser_type = request.args.get("browser_type")
    print("RECEIVED JSON DATA: ",data)
    timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
    
    # test_data = {
    #     "pin_code": "64347",
    #     "id_target": [26],
    #     "target_service_group": [],
    #     "service_name": [],

    #     "target_manufacturer": "FORD",
    #     "target_model": "KA",
    #     "target_year": "2011",

    #     "quantity_amount": "1",
    #     "target_date": "12.06.2025",
    #     "engine": "electric", 
        
    #     "your_data": {
    #         "firstName": "Dominik",
    #         "lastName": "Skakuj",
    #         "email": "dominik.skakuj1234@gmail.com",
    #         "mobile": "11111111111",
    #         "Erreichbarkeit": "",
    #         "licensePlate": "Da HI 2001",
    #         "HSN": "",
    #         "TSN": "",
    #         "mileage": "",
    #         "Radeinlagerungsnummer": "",
    #         "Firmenname": "",
    #         "Kundennummer": "",
    #         "Anmerkung": ""
    #     },
    
    # }

    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    # Run scraper in a background thread
    # thread = Thread(target=run_scraper, args=(test_data,timestamp))
    thread = Thread(target=lambda: ATUScraper(data, timestamp, browser_type).run())
    thread.start()

    # p = Process(target=lambda: ATUScraper(data, timestamp, browser_type).run())
    # p.start()

    return jsonify({"status": "Scraper started", "timestamp": timestamp}), 200

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=False, host='0.0.0.0', port=8000)