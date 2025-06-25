import numpy as np
from sklearn.cluster import DBSCAN
from scipy.spatial.distance import cdist
from pythonosc import udp_client
import json

# The Cluster class
class Cluster:
    def __init__(self, id, center, radius):
        self.id = id
        self.center = center
        self.radius = radius
        self.alive = True
        self.life = 10

    def update(self, center, diag):
        """Update the cluster's center and radius."""
        self.center = center
        self.radius = diag / 2

    def kill(self):
        """Kill the cluster by marking it as dead."""
        self.alive = False

    def revive(self):
        """Revive the cluster by marking it as alive and resetting its life."""
        self.alive = True
        self.life = 10  # Reset lifespan when revived

# The ClusterTracker class
class ClusterTracker:
    def __init__(self, radius, width):
        self.radius = radius
        self.prev_clusters = {}  # Stores cluster ID → Cluster object
        self.next_cluster_id = 0  # Unique cluster ID counter
        self.width = width  # Width of the area to be tracked

    def find_clusters(self, points, diagonals):
        """Identify clusters using DBSCAN."""
        if not points:
            return {}

        points_array = np.array(points)
        # Scanning for clusters using DBSCAN
        db = DBSCAN(eps=self.radius, min_samples=1).fit(points_array)
        labels = db.labels_

        clusters = {}
        # Group points by their cluster labels
        # Each cluster label corresponds to a unique cluster
        for point, diagonal, label in zip(points, diagonals, labels):
            if label == -1:
                continue  # Ignore noise points
            entry = clusters.setdefault(label, {"pts": [], "diags": []})
            entry["pts"].append(point)
            entry["diags"].append(diagonal)

        return clusters

    def match_clusters(self, new_clusters):
        """
        Match new clusters to existing ones.
        - Updates existing clusters if a match is found.
        - Revives clusters if they were previously marked as dead.
        - Marks unmatched clusters as dead.
        - Creates new clusters for unmatched new clusters.
        """
        updated_clusters = {}
        new_centroids   = []
        new_mean_diags  = []
        # Get previous cluster IDs and their centroids
        prev_ids = list(self.prev_clusters.keys())
        prev_centroids = [np.array(self.prev_clusters[cid].center) for cid in prev_ids]
        # Get new cluster labels
        new_labels = list(new_clusters.keys())
        for lbl in new_labels:
            # Extract points and diagonals for the new cluster
            pts   = np.array(new_clusters[lbl]["pts"])
            diags = np.array(new_clusters[lbl]["diags"])

            # centroid for matching
            new_centroids.append(np.mean(pts, axis=0))

            # mean diagonal → use as diameter proxy
            new_mean_diags.append(float(np.mean(diags)) + 100*(len(new_clusters[lbl]["diags"]) - 1))

        used_new = set()

        if prev_ids and new_labels:
            # Find the distances between previous and new centroids
            distances = cdist(np.array(prev_centroids), np.array(new_centroids))
            for i, cid in enumerate(prev_ids):
                # Find the closest new cluster to the current previous cluster
                closest_idx = np.argmin(distances[i])
                # If the closest new cluster is within the radius, update the existing cluster
                if distances[i][closest_idx] <= self.radius:
                    # Get the label of the closest new cluster
                    new_label = new_labels[closest_idx]
                    if new_label not in used_new:
                        # Update the existing cluster with new centroid and diagonal
                        self.prev_clusters[cid].update(new_centroids[closest_idx], new_mean_diags[closest_idx])
                        self.prev_clusters[cid].revive()  # Bring back to life
                        updated_clusters[cid] = self.prev_clusters[cid]
                        used_new.add(new_label)
                    else:
                        # If the new cluster was already used, we kill the previous cluster (two clusters merge)
                        self.prev_clusters[cid].kill()
                        updated_clusters[cid] = self.prev_clusters[cid]
                else:
                    # If no match is found, mark the previous cluster as dead
                    self.prev_clusters[cid].kill()
                    updated_clusters[cid] = self.prev_clusters[cid]
            # Each time we put a label, we remove that cluster from new_clusters
            for label in used_new:
                new_clusters.pop(label)
        # All remaining new clusters that were not removed are considered new clusters
        for label, item in new_clusters.items():
            centroid = np.mean(np.array(item["pts"]), axis=0)
            diagonal = np.mean(np.array(item["diags"])) + 100*(len(item["diags"]) - 1)  
            new_cluster = Cluster(self.next_cluster_id, centroid, diagonal/2)
            updated_clusters[new_cluster.id] = new_cluster
            self.next_cluster_id += 1

        return updated_clusters

    def update(self, points, diagonals):
        """
        Update clusters based on the current set of points.
        If a cluster disappears, it is marked as dead but not immediately removed.
        Only clusters with life <= 0 are removed.
        """
        new_clusters = self.find_clusters(points, diagonals)

        if new_clusters:
            self.prev_clusters = self.match_clusters(new_clusters)
        else:
            for cluster in self.prev_clusters.values():
                cluster.kill()  # Mark as dead

        # Remove clusters only when their life reaches 0
        self.prev_clusters = {cid: cluster for cid, cluster in self.prev_clusters.items() if cluster.life > 0}

    def decrease_life(self):
        """Decrease the life of dead clusters. Once life reaches 0, they are removed in update()."""
        for cluster in self.prev_clusters.values():
            if not cluster.alive:
                cluster.life -= 1
                print(f"Cluster {cluster.id} life decreased to {cluster.life}.")

    def get_cluster_centers_dict(self):
        """
        Returns a dict of cluster info normalized to [-1..1] for center coordinates and [0..1] for radius.:
        cluster_id → {
            "center": (x_norm, y_norm),   # each in [-1..1]
            "radius": r_norm              # fraction of frame width
        }
        """
        info = {}
        for cid, cluster in self.prev_clusters.items():
            cx, cy = cluster.center
            # normalize radius to [0..1] by width
            r_norm = float(cluster.radius) / float(self.width)

            info[cid] = {
                "center": ((2 * float(cx)/float(self.width)) - 1, (2 * float(cy)/float(self.width)) - 1),
                "radius": r_norm
            }
        return info


# OSC client setup
# osc_address = "192.168.1.146"
# osc_port = 7000
# osc_client = udp_client.SimpleUDPClient(osc_address, osc_port)

# Testing with disappearing and reappearing clusters
# tracker = ClusterTracker(radius=0.3)

# test_data = [
#     [(0.1, 0.2), (0.2, 0.2), (0.8, 0.9)],  # Time 1 - Initial clusters
#     [(0.1, 0.2), (0.2, 0.2)],  # Time 2 - One cluster missing
#     [(0.1, 0.2)],  # Time 3 - More clusters missing
#     [],  # Time 4 - All clusters missing
#     [],  # Time 5 - Still missing
#     [(0.8, 0.9)],  # Time 6 - Reappearing cluster
#     [(0.1, 0.2), (0.2, 0.2), (0.8, 0.9)]  # Time 7 - Everything back
# ]

# for i, points in enumerate(test_data):
#     print(f"\nTime {i+1}: Updating clusters with points: {points}")
#     tracker.update(points)
#     tracker.decrease_life()
#     print(tracker.get_cluster_centers_dict())

#     # Sending OSC message
#     osc_client.send_message("/clusters", json.dumps(tracker.get_cluster_centers_dict()))
