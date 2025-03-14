# Set your network and OSC address (adjust as needed)
NET_ADDRESS = "127.0.0.1"  # Example network address
OSC_ADDRESS = "/clusters"

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
    # We assume that the header is in column 0 and we want to delete all columns >0.
    while table.numCols > 1:
        table.deleteCol(1)
    
    # For each cluster, append a new column with its x, y, and scale values.
    for cluster in clusters:
        # Create a list for the new column's cells.
        # Converting values to strings is usually safe, as the TableDAT stores cell values as strings.
        col_data = [str(cluster.center[0]), str(cluster.center[1]), str(cluster.scale)]
        table.appendCol(col_data)

# Example usage:
if __name__ == "__main__":
    # Simulate receiving an OSC message with clusters
    # Example: Received clusters with ids 1 and 2.
    osc_message = {
        2: (100, 150),
        1: (200, 250)
    }
    update_clusters(osc_message)

    osc_message = {
        1: (105, 155),
        3: (200, 350),
        2: (300, 350)
    }
    update_clusters(osc_message)

    # Simulate a later OSC message where cluster 1 is updated, cluster 2 is missing (and should be killed),
    # and a new cluster 3 appears.
    osc_message = {
        3: (105, 155),
        1: (400, 350)
    }
    update_clusters(osc_message)

    table = op('table1')
    update_tableDAT_from_clusters(table, clusters_list)
