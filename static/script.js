let cy;

document.addEventListener("DOMContentLoaded", () => {
    // Initialize Cytoscape.js DAG
    cy = cytoscape({
        container: document.getElementById('cy'),
        elements: [
            // Nodes
            { data: { id: 'Power_Supply', label: 'Power Supply' } },
            { data: { id: 'Router_Status', label: 'Router' } },
            { data: { id: 'Switch_Status', label: 'Switch' } },
            { data: { id: 'Packet_Loss', label: 'Packet Loss' } },
            { data: { id: 'Network_Latency', label: 'Latency' } },
            { data: { id: 'Application_Status', label: 'App Status' } },
            { data: { id: 'Server_Load', label: 'Server Load' } },
            { data: { id: 'Server_Status', label: 'Server Status' } },
            { data: { id: 'Database_Status', label: 'Database' } },
            { data: { id: 'DNS_Status', label: 'DNS' } },
            { data: { id: 'Firewall_Status', label: 'Firewall' } },
            
            // Edges
            { data: { source: 'Power_Supply', target: 'Router_Status' } },
            { data: { source: 'Power_Supply', target: 'Switch_Status' } },
            { data: { source: 'Power_Supply', target: 'Server_Status' } },
            { data: { source: 'Router_Status', target: 'Packet_Loss' } },
            { data: { source: 'Switch_Status', target: 'Packet_Loss' } },
            { data: { source: 'Packet_Loss', target: 'Network_Latency' } },
            { data: { source: 'Network_Latency', target: 'Application_Status' } },
            { data: { source: 'Server_Load', target: 'Server_Status' } },
            { data: { source: 'Server_Status', target: 'Application_Status' } },
            { data: { source: 'Server_Status', target: 'Database_Status' } },
            { data: { source: 'Database_Status', target: 'Application_Status' } },
            { data: { source: 'DNS_Status', target: 'Application_Status' } },
            { data: { source: 'Firewall_Status', target: 'Application_Status' } }
        ],
        style: [
            {
                selector: 'node',
                style: {
                    'background-color': '#3b82f6',
                    'label': 'data(label)',
                    'color': '#fff',
                    'text-valign': 'center',
                    'text-halign': 'center',
                    'font-size': '10px',
                    'width': '60px',
                    'height': '30px',
                    'shape': 'round-rectangle',
                    'transition-property': 'background-color, transform',
                    'transition-duration': '0.5s'
                }
            },
            {
                selector: 'edge',
                style: {
                    'width': 2,
                    'line-color': '#475569',
                    'target-arrow-color': '#475569',
                    'target-arrow-shape': 'triangle',
                    'curve-style': 'bezier',
                    'transition-property': 'line-color, target-arrow-color, width',
                    'transition-duration': '0.5s'
                }
            },
            {
                selector: '.highlighted',
                style: {
                    'background-color': '#ef4444',
                    'line-color': '#ef4444',
                    'target-arrow-color': '#ef4444',
                    'width': 4,
                    'transform': 'scale(1.2)'
                }
            },
            {
                selector: '.most-probable',
                style: {
                    'background-color': '#8b5cf6',
                    'line-color': '#8b5cf6',
                    'target-arrow-color': '#8b5cf6',
                    'width': 4,
                    'transform': 'scale(1.3)'
                }
            }
        ],
        layout: {
            name: 'breadthfirst',
            directed: true,
            padding: 10
        }
    });
});

document.getElementById('diagnosisForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const loader = document.getElementById('loader');
    const btnText = document.querySelector('.primary-btn span');
    
    // UI Loading state
    loader.classList.remove('hidden');
    btnText.textContent = 'Diagnosing...';
    
    // Reset graph highlights
    cy.elements().removeClass('highlighted most-probable');
    
    const formData = new FormData(e.target);
    const data = Object.fromEntries(formData.entries());
    
    try {
        const response = await fetch('/api/diagnose', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayResults(result.results);
            animateGraph(result.results);
        } else {
            alert('Error running diagnosis: ' + result.error);
        }
    } catch (err) {
        alert('Server error: ' + err.message);
    } finally {
        // Reset UI
        loader.classList.add('hidden');
        btnText.textContent = 'Run Diagnosis';
    }
});

function displayResults(results) {
    const container = document.getElementById('resultsContainer');
    container.innerHTML = '';
    
    if (results.length === 0) {
        container.innerHTML = '<div class="empty-state"><p>No results found.</p></div>';
        return;
    }

    results.forEach((item, index) => {
        const isHighest = index === 0;
        const color = isHighest ? 'var(--primary)' : 'var(--secondary)';
        
        const card = document.createElement('div');
        card.className = 'result-card';
        card.innerHTML = `
            <div class="result-info">
                <h3>${item.cause} ${isHighest ? '🔥' : ''}</h3>
            </div>
            <div class="prob-container">
                <div class="prob-bar-bg">
                    <div class="prob-bar-fill" style="width: 0%; background: ${color}"></div>
                </div>
                <div class="prob-value" style="color: ${color}">${item.probability}%</div>
            </div>
        `;
        
        container.appendChild(card);
        
        // Trigger animation
        setTimeout(() => {
            card.querySelector('.prob-bar-fill').style.width = `${item.probability}%`;
        }, 50 * index);
    });
}

function animateGraph(results) {
    if (results.length === 0) return;
    
    // Map causes back to nodes
    const causeToNode = {
        "Power Instability": "Power_Supply",
        "Router Fault": "Router_Status",
        "Switch Fault": "Switch_Status",
        "Server Failure": "Server_Status",
        "Database Corruption": "Database_Status",
        "DNS Fault": "DNS_Status",
        "Firewall Blocking": "Firewall_Status"
    };

    // The most probable cause gets a special highlight
    const topCause = results[0];
    const topNodeId = causeToNode[topCause.cause];
    
    if (topNodeId) {
        // Highlight the node
        const node = cy.getElementById(topNodeId);
        node.addClass('most-probable');
        
        // Highlight the path to Application_Status using Dijkstra
        const dijkstra = cy.elements().dijkstra(node, () => 1, true);
        const path = dijkstra.pathTo(cy.getElementById('Application_Status'));
        
        let i = 0;
        const highlightNext = () => {
            if (i < path.length) {
                path[i].addClass('most-probable');
                i++;
                setTimeout(highlightNext, 200); // 200ms delay per edge/node
            }
        };
        highlightNext();
    }
}
