# IT Support Diagnostic Dashboard 🩺

This project is a probabilistic failure diagnosis system built for IT Helpdesks using **Bayesian Networks**. It features a modern, responsive web application that calculates the probability of various root causes (like server failures, DNS faults, or database corruption) based on observed symptoms (latency, packet loss, etc.).

## 📖 Theory & Concepts: Learn from this Project

This project is a practical application of **Probabilistic Graphical Models**, specifically **Bayesian Networks**.

### 1. Bayesian Networks (BNs)
A Bayesian Network is a probabilistic model that represents a set of variables and their conditional dependencies using a **Directed Acyclic Graph (DAG)**. 
- **Nodes** represent variables (e.g., `Server_Status`, `Network_Latency`).
- **Edges (arrows)** represent direct causal relationships (e.g., a faulty Server directly causes the Application to go down).

### 2. The Directed Acyclic Graph (DAG) Structure
Our diagnostic model is structured as shown in the diagram below. You can read the arrows as "influences" or "causes":

![Bayesian Network DAG](dag.png)

As seen in the photo, the network consists of:
- **Root / Input Nodes (Possible Causes):** Router Status, Server Load, DNS Status, and Firewall Status.
- **Intermediate Nodes (Observed Conditions):** Packet Loss, Network Latency, and Server Status.
- **Final Diagnostic Node (Target Variable):** Application Status.

### 3. Conditional Probability Tables (CPTs)
Every node in the graph has a CPT that dictates the probability of it being in a certain state, given the states of its parents. 
* *Example:* If the `Server Load` is High, what is the probability that the `Server Status` becomes "Failed"? 
In this project, instead of hardcoding these tables, we use a synthetic dataset (`network_incidents.csv`) and use **Maximum Likelihood Estimation (MLE)** via the `pgmpy` library to automatically learn the CPTs from the data!

### 4. Diagnostic Inference
When an IT operator inputs "Evidence" (e.g., `Application Status = Down` and `Packet Loss = High`), the system uses an algorithm called **Variable Elimination**. It works backwards through the network to calculate the *posterior probability* of the unobserved root causes (e.g., what is the probability that the Router is Faulty given what we just observed?).

---

## 🚀 Setup Instructions

1. Ensure you have Python installed.
2. Install the required dependencies:
   ```bash
   pip install flask flask-cors pandas numpy pgmpy streamlit
   ```

## 🌐 Running the Web Application (Flask)

The Flask application serves a beautiful, responsive, clinical-styled dashboard with an interactive Cytoscape.js network graph.

To run it:
```bash
python backend_api.py
```
Then, open your browser and navigate to: `http://localhost:5000`

### Viewing Analytical CPTs
While the web app is running, you can click the "📊 View Analytical CPTs" button to view the actual conditional probability distributions that the model learned from the dataset for every single node.

## 📊 Running the Streamlit App (Alternative View)

The Streamlit app provides an alternative data-science-focused interface.

To run it:
```bash
streamlit run app.py
```
Then, open your browser and navigate to the URL provided in the terminal (usually `http://localhost:8501`).

## 📱 Responsive Design Features

The web application (Flask + HTML/CSS) has been designed with responsiveness in mind:
- **CSS Grid:** The main `.dashboard` layout uses CSS Grid and automatically collapses from a two-column layout into a single column on mobile devices.
- **Flexbox:** Flexbox is used for result cards to ensure dynamic scaling of the probability bars.
