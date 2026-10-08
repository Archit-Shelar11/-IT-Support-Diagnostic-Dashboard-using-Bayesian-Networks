from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
from model_logic import NetworkDiagnosisModel

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)

print("Initializing Bayesian Network Model...")
model = NetworkDiagnosisModel()
print("Model initialized.")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/cpts')
def cpts():
    cpds = model.model.get_cpds()
    cpt_data = []
    for cpd in cpds:
        cpt_data.append({
            'variable': cpd.variable,
            'table': str(cpd)
        })
    return render_template('cpts.html', cpts=cpt_data)

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    data = request.json
    evidence = {}
    
    # Clean up evidence (remove empty/Unknown)
    for k, v in data.items():
        if v and v != "Unknown":
            evidence[k] = v
            
    try:
        results = model.diagnose(evidence)
        return jsonify({"success": True, "results": results, "evidence": evidence})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/dataset', methods=['GET'])
def get_dataset():
    sample = model.get_dataset_sample(10)
    return jsonify({"success": True, "data": sample})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
