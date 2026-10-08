import pandas as pd
import numpy as np
import os
from pgmpy.models import DiscreteBayesianNetwork
from pgmpy.estimators import MaximumLikelihoodEstimator
from pgmpy.inference import VariableElimination
from generate_dataset import generate_network_dataset

class NetworkDiagnosisModel:
    def __init__(self):
        self.model = None
        self.infer = None
        self.df = None
        self._initialize()

    def _initialize(self):
        if not os.path.exists('network_incidents.csv'):
            generate_network_dataset()
        
        self.df = pd.read_csv('network_incidents.csv')
        
        # Define the Network Structure (DAG)
        self.model = DiscreteBayesianNetwork([
            ('Power_Supply', 'Router_Status'),
            ('Power_Supply', 'Switch_Status'),
            ('Power_Supply', 'Server_Status'),
            ('Router_Status', 'Packet_Loss'),
            ('Switch_Status', 'Packet_Loss'),
            ('Packet_Loss', 'Network_Latency'),
            ('Network_Latency', 'Application_Status'),
            ('Server_Load', 'Server_Status'),
            ('Server_Status', 'Database_Status'),
            ('Server_Status', 'Application_Status'),
            ('Database_Status', 'Application_Status'),
            ('DNS_Status', 'Application_Status'),
            ('Firewall_Status', 'Application_Status')
        ])
        
        # Learn CPTs from data
        self.model.fit(self.df)
        
        # Initialize Inference object
        self.infer = VariableElimination(self.model)

    def diagnose(self, evidence):
        """
        Runs diagnostic inference given a set of evidence.
        Returns a sorted list of dictionaries with causes and their probabilities.
        """
        causes = {
            "Power Instability": ("Power_Supply", "Unstable"),
            "Router Fault": ("Router_Status", "Faulty"),
            "Switch Fault": ("Switch_Status", "Faulty"),
            "Server Failure": ("Server_Status", "Failed"),
            "Database Corruption": ("Database_Status", "Corrupt"),
            "DNS Fault": ("DNS_Status", "Faulty"),
            "Firewall Blocking": ("Firewall_Status", "Blocking")
        }
        
        results = []
        for cause_name, (var, state) in causes.items():
            if var in evidence:
                # If the variable is already in evidence, we know its state exactly.
                prob = 1.0 if evidence[var] == state else 0.0
            else:
                res = self.infer.query(variables=[var], evidence=evidence)
                prob = res.values[res.state_names[var].index(state)]
                
            results.append({
                "cause": cause_name, 
                "probability": round(prob * 100, 2)
            })
            
        # Sort by highest probability
        results = sorted(results, key=lambda x: x["probability"], reverse=True)
        return results

    def get_dataset_sample(self, n=10):
        return self.df.head(n).to_dict(orient='records')
