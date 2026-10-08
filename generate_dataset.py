import pandas as pd
import numpy as np

def generate_network_dataset(num_samples=5000):
    np.random.seed(42)
    
    # 1. Power Supply: Normal (95%), Unstable (5%)
    power_supply = np.random.choice(['Normal', 'Unstable'], size=num_samples, p=[0.95, 0.05])

    # 2. Router Status: Depends on Power Supply
    router_status = np.where(
        power_supply == 'Normal',
        np.random.choice(['Healthy', 'Faulty'], size=num_samples, p=[0.95, 0.05]),
        np.random.choice(['Healthy', 'Faulty'], size=num_samples, p=[0.50, 0.50])
    )

    # 3. Switch Status: Depends on Power Supply
    switch_status = np.where(
        power_supply == 'Normal',
        np.random.choice(['Healthy', 'Faulty'], size=num_samples, p=[0.98, 0.02]),
        np.random.choice(['Healthy', 'Faulty'], size=num_samples, p=[0.60, 0.40])
    )
    
    # 4. Packet Loss: Depends on Router and Switch
    packet_loss = []
    for r, s in zip(router_status, switch_status):
        if r == 'Faulty' or s == 'Faulty':
            packet_loss.append(np.random.choice(['Low', 'High'], p=[0.10, 0.90]))
        else:
            packet_loss.append(np.random.choice(['Low', 'High'], p=[0.95, 0.05]))
    packet_loss = np.array(packet_loss)
    
    # 5. Network Latency: Depends on Packet Loss
    network_latency = np.where(
        packet_loss == 'Low',
        np.random.choice(['Low', 'High'], size=num_samples, p=[0.90, 0.10]),
        np.random.choice(['Low', 'High'], size=num_samples, p=[0.25, 0.75])
    )
    
    # 6. Server Load: Low (70%), High (30%)
    server_load = np.random.choice(['Low', 'High'], size=num_samples, p=[0.70, 0.30])
    
    # 7. Server Status: Depends on Server Load and Power Supply
    server_status = []
    for sl, ps in zip(server_load, power_supply):
        if ps == 'Unstable':
            server_status.append(np.random.choice(['Healthy', 'Failed'], p=[0.40, 0.60]))
        elif sl == 'High':
            server_status.append(np.random.choice(['Healthy', 'Failed'], p=[0.70, 0.30]))
        else:
            server_status.append(np.random.choice(['Healthy', 'Failed'], p=[0.98, 0.02]))
    server_status = np.array(server_status)
    
    # 8. Database Status: Depends on Server Status
    db_status = np.where(
        server_status == 'Healthy',
        np.random.choice(['Available', 'Corrupt'], size=num_samples, p=[0.99, 0.01]),
        np.random.choice(['Available', 'Corrupt'], size=num_samples, p=[0.30, 0.70])
    )

    # 9. DNS Status: Healthy (95%), Faulty (5%)
    dns_status = np.random.choice(['Healthy', 'Faulty'], size=num_samples, p=[0.95, 0.05])
    
    # 10. Firewall Status: Normal (90%), Blocking (10%)
    firewall_status = np.random.choice(['Normal', 'Blocking'], size=num_samples, p=[0.90, 0.10])
    
    # 11. Application Status: Depends on Latency, Server, DB, DNS, Firewall
    application_status = []
    for lat, srv, db, dns, fw in zip(network_latency, server_status, db_status, dns_status, firewall_status):
        if fw == 'Blocking' or dns == 'Faulty' or srv == 'Failed' or db == 'Corrupt':
            application_status.append(np.random.choice(['Available', 'Down'], p=[0.02, 0.98]))
        elif lat == 'High':
            application_status.append(np.random.choice(['Available', 'Down'], p=[0.75, 0.25]))
        else:
            application_status.append(np.random.choice(['Available', 'Down'], p=[0.99, 0.01]))
            
    df = pd.DataFrame({
        'Power_Supply': power_supply,
        'Router_Status': router_status,
        'Switch_Status': switch_status,
        'Packet_Loss': packet_loss,
        'Network_Latency': network_latency,
        'Server_Load': server_load,
        'Server_Status': server_status,
        'Database_Status': db_status,
        'DNS_Status': dns_status,
        'Firewall_Status': firewall_status,
        'Application_Status': application_status
    })
    
    df.to_csv('network_incidents.csv', index=False)
    print(f"Generated network_incidents.csv with {num_samples} records.")

if __name__ == "__main__":
    generate_network_dataset()
