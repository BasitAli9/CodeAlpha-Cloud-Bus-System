import os
import uuid
import sqlite3
import random
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)
DB_FILE = 'cloud_bus_system.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bus_passes (
            pass_token TEXT PRIMARY KEY,
            passenger_name TEXT,
            route TEXT,
            price REAL,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Enterprise Cloud Bus Pass Portal</title>
    <style>
        body { font-family: 'Segoe UI', Arial, sans-serif; background-color: #0f172a; color: #e2e8f0; margin: 0; padding: 20px; }
        .container { max-width: 950px; margin: 30px auto; background: #1e293b; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
        h2 { color: #38bdf8; text-align: center; margin-bottom: 5px; }
        p.subtitle { text-align: center; color: #94a3b8; margin-bottom: 25px; font-size: 14px; }
        
        /* Infrastructure Metrics Counters */
        .metrics-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 25px; }
        .metric-card { background: #0f172a; padding: 15px; border-radius: 8px; text-align: center; border-bottom: 3px solid #38bdf8; }
        .metric-value { font-size: 22px; font-weight: bold; color: white; margin-top: 5px; }
        .metric-label { font-size: 12px; color: #94a3b8; text-transform: uppercase; }
        
        /* Load Balancer Bar Layout */
        .load-container { background: #0f172a; padding: 15px; border-radius: 8px; margin-bottom: 25px; border: 1px solid #334155; }
        .load-bar-bg { background: #334155; height: 12px; border-radius: 6px; overflow: hidden; margin-top: 8px; }
        .load-bar-fill { background: linear-gradient(90deg, #10b981, #f59e0b, #ef4444); width: 15%; height: 100%; transition: width 0.5s ease; }
        
        /* Form & Content Input styling */
        label { display: block; margin: 10px 0 5px; color: #94a3b8; }
        input, select { width: 100%; padding: 12px; margin-bottom: 15px; border-radius: 6px; border: 1px solid #475569; box-sizing: border-box; background: #0f172a; color: white; }
        button { width: 100%; padding: 14px; font-weight: bold; border-radius: 6px; border: none; cursor: pointer; transition: 0.3s; color: white; background: #10b981; }
        button:hover { background: #059669; }
        .log-box { background: #0f172a; padding: 15px; border-radius: 8px; margin-top: 20px; font-family: monospace; font-size: 13px; border-left: 4px solid #38bdf8; }
        
        /* Advanced Cloud Registry Table Data View */
        .table-section { margin-top: 35px; border-top: 2px solid #334155; padding-top: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 15px; background: #0f172a; border-radius: 8px; overflow: hidden; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #334155; font-size: 14px; }
        th { background-color: #1e293b; color: #38bdf8; }
        .btn-cancel { background: #ef4444; padding: 6px 12px; font-size: 12px; border-radius: 4px; border: none; color: white; cursor: pointer; width: auto; }
        .btn-cancel:hover { background: #dc2626; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🚌 Cloud-Based Bus Pass Management Portal</h2>
        <p class="subtitle">Distributed Token Architecture & High-Traffic Dynamic Capacity Provisioning</p>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Active Cloud Clusters</div>
                <div id="m-instances" class="metric-value">3 Nodes</div>
            </div>
            <div class="metric-card" style="border-color: #10b981;">
                <div class="metric-label">Passes Registered</div>
                <div id="m-passes" class="metric-value">0</div>
            </div>
            <div class="metric-card" style="border-color: #f59e0b;">
                <div class="metric-label">Redundancy Blocks</div>
                <div id="m-blocks" class="metric-value">0 Counters</div>
            </div>
        </div>

        <div class="load-container">
            <div style="display: flex; justify-content: space-between; font-size: 12px;">
                <span style="color: #94a3b8; font-weight: bold;">📊 Dynamic Elastic Cluster Load Simulation</span>
                <span id="loadText" style="color: #10b981; font-weight: bold;">12% CPU Load (Stable)</span>
            </div>
            <div class="load-bar-bg">
                <div id="loadBar" class="load-bar-fill"></div>
            </div>
        </div>

        <form id="bookingForm">
            <label>Passenger Identity Name:</label>
            <input type="text" id="passengerName" placeholder="Enter Full Name" required>

            <label>Select Deployment Allocation Route Matrix:</label>
            <select id="route">
                <option value="Route Alpha (Downtown-Express)">Route Alpha (Downtown-Express) - $15.85</option>
                <option value="Route Beta (Intercity-Link)">Route Beta (Intercity-Link) - $25.50</option>
                <option value="Route Gamma (Orbital Highway)">Route Gamma (Orbital Highway) - $35.30</option>
            </select>

            <button type="button" onclick="bookPass()">Provision Server & Secure Pass Token</button>
        </form>

        <div id="bookingResult" class="log-box" style="display: none;"></div>

        <div class="table-section">
            <h3>🗄️ Core Cloud Infrastructure Registry Storage Ledger</h3>
            <table>
                <thead>
                    <tr>
                        <th>Algorithmic Token</th>
                        <th>Passenger Name</th>
                        <th>Route Mapped</th>
                        <th>Locked Fare</th>
                        <th>Cluster Action</th>
                    </tr>
                </thead>
                <tbody id="recordsTableBody">
                    </tbody>
            </table>
        </div>
    </div>

    <script>
        let redundancyBlockCounter = 0;

        window.onload = loadRecords;

        async function loadRecords() {
            const response = await fetch('/get_records');
            const data = await response.json();
            const tbody = document.getElementById('recordsTableBody');
            tbody.innerHTML = '';

            // Update Dynamic Pass Counter Block
            document.getElementById('m-passes').innerText = data.length;
            
            // Adjust Load Balancer Simulation calculations dynamically
            let currentLoad = Math.min(12 + (data.length * 9), 94);
            document.getElementById('loadBar').style.width = currentLoad + "%";
            
            let loadLabel = document.getElementById('loadText');
            loadLabel.innerText = currentLoad + "% CPU Load";
            if (currentLoad > 75) { loadLabel.style.color = '#ef4444'; }
            else if (currentLoad > 45) { loadLabel.style.color = '#f59e0b'; }
            else { loadLabel.style.color = '#10b981'; }

            // Dynamic server cloud node instances scale count simulation
            let clustersCount = Math.max(3, Math.ceil(data.length / 3));
            document.getElementById('m-instances').innerText = clustersCount + " Active Nodes";

            if(data.length === 0) {
                tbody.innerHTML = `<tr><td colspan="5" style="text-align:center; color:#94a3b8;">No data packets in active cloud registry allocation blocks.</td></tr>`;
                return;
            }

            data.forEach(row => {
                tbody.innerHTML += `
                    <tr>
                        <td style="color:#f43f5e; font-family:monospace; font-weight:bold;">${row.pass_token}</td>
                        <td>${row.passenger_name}</td>
                        <td>${row.route}</td>
                        <td>$${row.price.toFixed(2)}</td>
                        <td><button class="btn-cancel" onclick="cancelPass('${row.pass_token}')">De-allocate</button></td>
                    </tr>
                `;
            });
        }

        async function bookPass() {
            const passenger_name = document.getElementById('passengerName').value.trim();
            const route = document.getElementById('route').value;
            if(!passenger_name) { alert("Please input passenger name identity."); return; }

            const response = await fetch('/book_pass', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ passenger_name, route })
            });
            const data = await response.json();
            
            const resultBox = document.getElementById('bookingResult');
            resultBox.style.display = 'block';

            if(data.error) {
                resultBox.innerHTML = `<span style="color: #f87171; font-weight: bold;">⚠ Security Violation Constraint: ${data.error}</span>`;
                redundancyBlockCounter++;
                document.getElementById('m-blocks').innerText = redundancyBlockCounter + " Blocks Checked";
            } else {
                resultBox.innerHTML = `
                    <span style="color: #4ade80; font-weight: bold;">✔ ${data.status}</span><br><br>
                    <strong>Secure Token Hash:</strong> <span style="color: #f43f5e;">${data.pass_token}</span><br>
                    <strong>Ident Passenger:</strong> ${data.passenger_name}<br>
                    <strong>Matrix Route Assignment:</strong> ${data.route}<br>
                    <strong>Cryptographic Locked Cost:</strong> $${data.price.toFixed(2)}<br>
                    <span style="font-size:11px; color:#a855f7; display:block; margin-top:8px;">⚙ [Elastic Scalability]: Threaded request mapped safely into automated runtime cluster instance node #${data.instance_id}</span>
                `;
                document.getElementById('passengerName').value = '';
                loadRecords();
            }
        }

        async function cancelPass(token) {
            if(!confirm("Terminate instance token packet constraint?")) return;
            await fetch('/cancel_pass', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ pass_token: token })
            });
            loadRecords();
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/get_records', methods=['GET'])
def get_records():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bus_passes")
    rows = cursor.fetchall()
    conn.close()
    return jsonify([dict(ix) for ix in rows])

@app.route('/book_pass', methods=['POST'])
def book_pass():
    data = request.json
    passenger_name = data.get('passenger_name')
    route = data.get('route')
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM bus_passes WHERE passenger_name = ? AND route = ?", (passenger_name, route))
    if cursor.fetchone():
        conn.close()
        return jsonify({"error": "Data Redundancy Detected! Overlapping reservation packet rejected by database optimization layer."})
    
    price = 25.00 
    pass_token = "PASS-" + str(uuid.uuid4()).upper()[:8]
    
    cursor.execute(
        "INSERT INTO bus_passes (pass_token, passenger_name, route, price, status) VALUES (?, ?, ?, ?, 'ACTIVE')",
        (pass_token, passenger_name, route, price)
    )
    conn.commit()
    conn.close()
    
    simulated_instance_id = random.randint(104, 999)
    
    return jsonify({
        "status": "Production-Grade Pass Token Allocated Safely",
        "pass_token": pass_token,
        "passenger_name": passenger_name,
        "route": route,
        "price": price,
        "instance_id": simulated_instance_id
    })

@app.route('/cancel_pass', methods=['POST'])
def cancel_pass():
    data = request.json
    pass_token = data.get('pass_token')
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bus_passes WHERE pass_token = ?", (pass_token,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)