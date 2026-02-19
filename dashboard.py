import streamlit as st
import sqlite3
import pandas as pd
import os

# Page Config
st.set_page_config(
    page_title="Ethical AI Pentest Dashboard",
    page_icon="🛡️",
    layout="wide"
)

# Title and Header
st.title("🛡️ Ethical AI Pentest Dashboard")
st.markdown("Monitor your active engagement, discovered assets, and vulnerabilities in real-time.")

# Database Connection
DB_PATH = "pentest_data.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def load_data():
    if not os.path.exists(DB_PATH):
        return None, None, None
        
    conn = get_connection()
    
    try:
        targets_df = pd.read_sql("SELECT * FROM targets", conn)
        ports_df = pd.read_sql("SELECT * FROM ports", conn)
        vulns_df = pd.read_sql("SELECT * FROM vulnerabilities", conn)
    except Exception as e:
        st.error(f"Error reading database: {e}")
        return None, None, None
    finally:
        conn.close()
        
    return targets_df, ports_df, vulns_df

# Load Data
targets, ports, vulns = load_data()

if targets is None:
    st.warning("⚠️ Database not found or empty. Run a scan first!")
    st.stop()

# Sidebar
st.sidebar.header("Navigation")
view_option = st.sidebar.radio("Go to", ["Overview", "Targets", "Vulnerabilities", "Network Map"])

st.sidebar.markdown("---")
st.sidebar.markdown(f"**Total Targets:** {len(targets)}")
st.sidebar.markdown(f"**Total Services:** {len(ports)}")
st.sidebar.markdown(f"**Total Vulns:** {len(vulns)}")

# Overview Page
if view_option == "Overview":
    st.header("Engagement Overview")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Targets", len(targets))
    
    with col2:
        up_hosts = len(targets[targets['status'] == 'Up'])
        st.metric("Hosts Up", up_hosts)
        
    with col3:
        crit_vulns = len(vulns[vulns['severity'] == 'CRITICAL']) if not vulns.empty else 0
        st.metric("Critical Vulns", crit_vulns, delta_color="inverse")
        
    with col4:
        high_vulns = len(vulns[vulns['severity'] == 'HIGH']) if not vulns.empty else 0
        st.metric("High Vulns", high_vulns, delta_color="inverse")

    # Recent Activity / Vulnerability Severity Distribution
    col_chart1, col_chart2 = st.columns(2)
    
    with col_chart1:
        st.subheader("Top Operating Systems")
        if not targets.empty and 'os_info' in targets.columns:
            os_counts = targets['os_info'].value_counts()
            st.bar_chart(os_counts)
        else:
            st.info("No OS data available.")

    with col_chart2:
        st.subheader("Vulnerability Severity")
        if not vulns.empty:
            severity_counts = vulns['severity'].value_counts()
            st.bar_chart(severity_counts)
        else:
            st.success("No vulnerabilities found yet.")

# Targets Page
elif view_option == "Targets":
    st.header("Discovered Assets")
    
    if not targets.empty:
        st.dataframe(targets, use_container_width=True)
        
        selected_ip = st.selectbox("Select Target to View Details", targets['ip_address'])
        
        if selected_ip:
            target_id = targets[targets['ip_address'] == selected_ip]['id'].values[0]
            st.subheader(f"Details for {selected_ip}")
            
            # Show Ports for this target
            target_ports = ports[ports['target_id'] == target_id]
            if not target_ports.empty:
                st.markdown("#### Open Ports")
                st.table(target_ports[['port_number', 'protocol', 'service_name', 'version', 'state']])
            else:
                st.info("No open ports found for this target.")
                
            # Show Vulns for this target
            target_vulns = vulns[vulns['target_id'] == target_id]
            if not target_vulns.empty:
                st.markdown("#### Vulnerabilities")
                for _, row in target_vulns.iterrows():
                    color = "red" if row['severity'] in ['CRITICAL', 'HIGH'] else "orange"
                    st.markdown(f":{color}[**{row['severity']}**] - {row['name']}")
                    st.caption(row['description'])
                    st.markdown("---")
            else:
                st.success("No vulnerabilities linked to this target.")

# Vulnerabilities Page
elif view_option == "Vulnerabilities":
    st.header("Vulnerability Report")
    
    if not vulns.empty:
        # Filter
        severity_filter = st.multiselect(
            "Filter by Severity", 
            options=vulns['severity'].unique(),
            default=vulns['severity'].unique()
        )
        
        filtered_vulns = vulns[vulns['severity'].isin(severity_filter)]
        
        # Display as cards
        for _, row in filtered_vulns.iterrows():
            with st.expander(f"{row['severity']} - {row['name']} (ID: {row['id']})"):
                st.markdown(f"**Description:** {row['description']}")
                # Lookup target IP
                t_row = targets[targets['id'] == row['target_id']]
                if not t_row.empty:
                    st.markdown(f"**Affected Target:** {t_row.iloc[0]['ip_address']}")
    else:
        st.success("No vulnerabilities found.")

# Refresh Button
if st.sidebar.button("Refresh Data"):
    st.rerun()

# ---------------------------------------------------------------------
# Network Map Logic
# ---------------------------------------------------------------------
import streamlit.components.v1 as components
from pyvis.network import Network
import tempfile

if view_option == "Network Map":
    st.header("Network Topology Map")
    st.markdown("Visualizing relationships between Targets and Open Ports.")

    if targets.empty:
        st.info("No targets to visualize.")
    else:
        # Create Network
        net = Network(height="600px", width="100%", bgcolor="#222222", font_color="white")
        
        # 1. Add Central Node (Attacker)
        net.add_node("Attacker (Kali)", label="Attacker (Kali)", color="#ff4b4b", shape="box")

        # 2. Add Target Nodes
        for _, target in targets.iterrows():
            t_label = f"{target['ip_address']}\n({target['hostname']})" if target['hostname'] else target['ip_address']
            t_color = "#00c0f2" # Blue
            if target['status'] != 'Up':
                t_color = "#555555" # Grey if down
            
            net.add_node(target['ip_address'], label=t_label, color=t_color, title=f"OS: {target.get('os_info', 'N/A')}")
            net.add_edge("Attacker (Kali)", target['ip_address'])

            # 3. Add Port Nodes linked to Target
            # Filter ports for this target
            t_ports = ports[ports['target_id'] == target['id']]
            for _, port in t_ports.iterrows():
                p_node_id = f"{target['ip_address']}:{port['port_number']}"
                p_label = f"{port['port_number']}/{port['protocol']}\n{port['service_name']}"
                p_color = "#ffa500" # Orange
                
                # Check if port has vuln? (Optional enhancement)
                
                net.add_node(p_node_id, label=p_label, color=p_color, shape="ellipse", size=10)
                net.add_edge(target['ip_address'], p_node_id)

        # Physics options for better stability
        net.barnes_hut()
        
        # Save and Read
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as tmp:
                net.save_graph(tmp.name)
                
                # Read content
                with open(tmp.name, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
            # Display
            components.html(html_content, height=620)
            
        except Exception as e:
            st.error(f"Error generating graph: {e}")

