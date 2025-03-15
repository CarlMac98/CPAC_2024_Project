import json
import numpy as np
from pythonosc import dispatcher, osc_server
from scipy.spatial.distance import cdist

# Set your network and OSC address (adjust as needed)
NET_ADDRESS = "127.0.0.1"  # Example network address
OSC_ADDRESS = "/clusters"
OSC_PORT = 8000          # Example port

# The cluster class as provided
class Cluster:
    def __init__(self, id, center):
        self.id = id
        self.center = center
        self.alive = True
        self.scale = 0 

    def update(self, center):
        self.center = center

    def kill(self):
        self.alive = False

    def check_scaling(self):
        if self.alive and self.scale < 1:
            self.scale += 0.1
        elif not self.alive and self.scale > 0:
            self.scale -= 0.1

    def completely_dead(self):
        return self.scale <= 0

# List to hold the existing clusters
clusters_list = []

def update_clusters(received_clusters):
    """
    Process the received OSC message that contains a dictionary of clusters.
    Each key is a cluster id and each value is a tuple with the cluster's coordinates.
    """
    global clusters_list

    # Extract the set of cluster IDs that were received
    received_ids = set(received_clusters.keys())

    # Process each cluster in the received message
    for cluster_id, center in received_clusters.items():
        # Search for an existing cluster with the same id
        existing_cluster = next((c for c in clusters_list if c.id == cluster_id), None)
        if existing_cluster is None:
            # Not found: create a new cluster with the provided id and center
            new_cluster = Cluster(cluster_id, center)
            clusters_list.append(new_cluster)
        else:
            # Found: update its center coordinates
            existing_cluster.update(center)

    # For clusters that were not in the OSC message, mark them as dead
    for cluster in clusters_list:
        if cluster.id not in received_ids:
            cluster.kill()

    # Call the scaling function for each cluster to update its animation state
    for cluster in clusters_list:
        cluster.check_scaling()

    # Remove clusters that have fully "scaled down" (completely dead)
    clusters_list = [cluster for cluster in clusters_list if not cluster.completely_dead()]
    
    # Ensure clusters are sorted by ID
    clusters_list.sort(key=lambda cluster: cluster.id)

    # (Optional) Print status for debugging
    print("Current clusters:")
    for cluster in clusters_list:
        print(f"ID: {cluster.id}, Center: {cluster.center}, Alive: {cluster.alive}, Scale: {cluster.scale}")

def update_tableDAT_from_clusters(table, clusters):
    """
    Updates a TableDAT operator 'table' with cluster data.
    The table already has three rows with headers:
       Row 0, Col 0: "x_axis"
       Row 1, Col 0: "y_axis"
       Row 2, Col 0: "scale"
       
    For each cluster in 'clusters', a new column is appended with:
       - First row: cluster.center[0]
       - Second row: cluster.center[1]
       - Third row: cluster.scale
    """
    # Remove previously appended cluster columns (if any)
    # We assume that the header is in column 0 and we want to delete all columns > 0.
    while table.numCols > 1:
        table.deleteCol(1)
    
    # For each cluster, append a new column with its x, y, and scale values.
    for cluster in clusters:
        col_data = [str(cluster.center[0]), str(cluster.center[1]), str(cluster.scale)]
        table.appendCol(col_data)

def osc_clusters_handler(address, *args):
    """
    OSC handler for the '/clusters' address.
    Expects the first argument to be a JSON-encoded string representing the clusters dictionary.
    """
    if not args:
        print("No OSC data received.")
        return
    try:
        # Convert JSON string to dictionary
        received_clusters = json.loads(args[0])
        print("Received clusters:", received_clusters)
        update_clusters(received_clusters)
    except Exception as e:
        print("Error processing OSC message:", e)

# Main section: either simulate OSC messages or start an OSC server.
if __name__ == "__main__":
    # --- Option 1: Simulate incoming OSC messages for testing ---
    test_messages = [
        {2: (100, 150), 1: (200, 250)},
        {1: (105, 155), 3: (200, 350), 2: (300, 350)},
        {3: (105, 155), 1: (400, 350)}
    ]
    for msg in test_messages:
        # Convert the dictionary to a JSON string and simulate an OSC message.
        osc_msg = json.dumps(msg)
        osc_clusters_handler(OSC_ADDRESS, osc_msg)

    # --- Option 2: Start the OSC server ---
    # Create an OSC dispatcher and map the OSC_ADDRESS to our handler.
    disp = dispatcher.Dispatcher()
    disp.map(OSC_ADDRESS, osc_clusters_handler)
    
    # Create and start the OSC server (this call blocks).
    server = osc_server.BlockingOSCUDPServer((NET_ADDRESS, OSC_PORT), disp)
    print(f"OSC server listening on {NET_ADDRESS}:{OSC_PORT}")
    
    # If running inside TouchDesigner, you could update your TableDAT like this:
    table = op('table1')
    update_tableDAT_from_clusters(table, clusters_list)
    
    server.serve_forever()
