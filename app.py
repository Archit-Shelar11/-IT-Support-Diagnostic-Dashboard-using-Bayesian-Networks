import streamlit as st
import pandas as pd
import numpy as np
import os
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator
from pgmpy.inference import VariableElimination
from generate_dataset import generate_network_dataset

st.set_page_config(page_title="Network Failure Diagnosis", page_icon="📡", layout="wide")

# Custom CSS for a premium look
st.markdown("""
<style>
    .stApp {
        background-color: #0e1117;
        color: #e0e0e0;
    }
    .stButton>button {
        background: linear-gradient(135deg, #6e8efb, #a777e3);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(167, 119, 227, 0.4);
    }
    div[data-testid="stSidebar"] {
        background-color: #1a1c24;
        border-right: 1px solid #2d3139;
    }
    h1, h2, h3 {
        color: #ffffff;
        font-family: 'Inter', sans-serif;
    }
    .stSelectbox label {
        color: #a0aabf;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_resource
def load_and_train_model():
    if not os.path.exists('network_incidents.csv'):
        generate_network_dataset()
    
    df = pd.read_csv('network_incidents.csv')
    
    # Define the Network Structure (DAG)
    model = DiscreteBayesianNetwork([
        ('Router_Status', 'Packet_Loss'),
        ('Packet_Loss', 'Network_Latency'),
        ('Network_Latency', 'Application_Status'),
        ('Server_Load', 'Server_Status'),
        ('Server_Status', 'Application_Status'),
        ('DNS_Status', 'Application_Status'),
        ('Firewall_Status', 'Application_Status')
    ])
    
    # Learn CPTs from data
    model.fit(df)
    
    # Initialize Inference object
    infer = VariableElimination(model)
    return model, infer, df

st.title("📡 Network Failure Diagnosis")
st.markdown("### Probabilistic Diagnostic System using Bayesian Networks")
st.markdown("This system diagnoses the most probable cause of application failure based on observed network conditions.")

with st.spinner("Loading Model & Generating Dataset..."):
    model, infer, df = load_and_train_model()

# ==================== UI ====================
st.sidebar.header("Observation Panel (Evidence)")

app_status = st.sidebar.selectbox("Application Status", ["Down", "Available"])
latency = st.sidebar.selectbox("Network Latency", ["Unknown", "Low", "High"])
packet_loss = st.sidebar.selectbox("Packet Loss", ["Unknown", "Low", "High"])
server_load = st.sidebar.selectbox("Server Load", ["Unknown", "Low", "High"])

# Prepare evidence dictionary
evidence = {}
if app_status != "Unknown": evidence['Application_Status'] = app_status
if latency != "Unknown": evidence['Network_Latency'] = latency
if packet_loss != "Unknown": evidence['Packet_Loss'] = packet_loss
if server_load != "Unknown": evidence['Server_Load'] = server_load


col1, col2 = st.columns(2)

with col1:
    st.subheader("Diagnostic Results")
    st.markdown("Given the evidence, what is the probability of each component being faulty?")
    
    if st.button("Run Diagnostic Inference"):
        with st.spinner("Calculating probabilities..."):
            causes = {
                "Router Fault": ("Router_Status", "Faulty"),
                "Server Failure": ("Server_Status", "Failed"),
                "DNS Fault": ("DNS_Status", "Faulty"),
                "Firewall Blocking": ("Firewall_Status", "Blocking")
            }
            
            results = []
            for cause_name, (var, state) in causes.items():
                res = infer.query(variables=[var], evidence=evidence)
                prob = res.values[res.state_names[var].index(state)]
                results.append({"Cause": cause_name, "Probability (%)": round(prob * 100, 2)})
            
            res_df = pd.DataFrame(results).sort_values(by="Probability (%)", ascending=False).reset_index(drop=True)
            
            st.dataframe(res_df, use_container_width=True)
            
            most_probable = res_df.iloc[0]['Cause']
            st.success(f"🔥 Most Probable Cause: **{most_probable}** ({res_df.iloc[0]['Probability (%)']}%)")

with col2:
    st.subheader("Explore the Dataset")
    st.markdown("This synthetic dataset of 5000 incidents is used to learn the Conditional Probability Tables (CPTs).")
    st.dataframe(df.head(10), use_container_width=True)
    
    st.subheader("What-If Analysis")
    st.markdown("Example: What is the normal probability of application failure without any evidence?")
    res_base = infer.query(variables=['Application_Status'])
    prob_down = res_base.values[res_base.state_names['Application_Status'].index('Down')]
    st.info(f"Baseline P(Application Down) = {prob_down*100:.2f}%")

