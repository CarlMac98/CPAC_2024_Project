import numpy as np
from sklearn.cluster import DBSCAN
from scipy.spatial.distance import cdist
from pythonosc import udp_client
import json

# The Cluster class
class Cluster:
    def __init__(self, id, center):
        self.id = id
        self.center = center
        self.alive = True
        self.life = 5  # Decreased lifespan for quicker testing

    def update(self, center):
        self.center = center

    def kill(self):
        self.alive = False

    def revive(self):
        """Revive the cluster by marking it as alive and resetting its life."""
        self.alive = True
        self.life = 5  # Reset lifespan when revived

# The ClusterTracker class
class ClusterTracker:
    def __init__(self, radius, width):
        self.radius = radius
        self.prev_clusters = {}  # Stores cluster ID → Cluster object
        self.next_cluster_id = 0  # Unique cluster ID counter
        self.width = width  # Width of the area to be tracked

    def find_clusters(self, points):
        """Identify clusters using DBSCAN."""
        if not points:
            return {}

        points_array = np.array(points)
        db = DBSCAN(eps=self.radius, min_samples=1).fit(points_array)
        labels = db.labels_

        clusters = {}
        for point, label in zip(points, labels):
            if label == -1:
                continue  # Ignore noise points
            clusters.setdefault(label, []).append(point)

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
        prev_ids = list(self.prev_clusters.keys())
        prev_centroids = [np.array(self.prev_clusters[cid].center) for cid in prev_ids]

        new_labels = list(new_clusters.keys())
        new_centroids = [np.mean(np.array(new_clusters[label]), axis=0) for label in new_labels]

        used_new = set()

        if prev_ids and new_labels:
            distances = cdist(np.array(prev_centroids), np.array(new_centroids))
            for i, cid in enumerate(prev_ids):
                closest_idx = np.argmin(distances[i])
                if distances[i][closest_idx] <= self.radius:
                    new_label = new_labels[closest_idx]
                    if new_label not in used_new:
                        self.prev_clusters[cid].update(new_centroids[closest_idx])
                        self.prev_clusters[cid].revive()  # Bring back to life
                        updated_clusters[cid] = self.prev_clusters[cid]
                        used_new.add(new_label)
                    else:
                        self.prev_clusters[cid].kill()
                        updated_clusters[cid] = self.prev_clusters[cid]
                else:
                    self.prev_clusters[cid].kill()
                    updated_clusters[cid] = self.prev_clusters[cid]

            for label in used_new:
                new_clusters.pop(label)

        for label, pts in new_clusters.items():
            centroid = np.mean(np.array(pts), axis=0)
            new_cluster = Cluster(self.next_cluster_id, centroid)
            updated_clusters[new_cluster.id] = new_cluster
            self.next_cluster_id += 1

        return updated_clusters

    def update(self, points):
        """
        Update clusters based on the current set of points.
        If a cluster disappears, it is marked as dead but not immediately removed.
        Only clusters with life <= 0 are removed.
        """
        new_clusters = self.find_clusters(points)

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
        """Returns a dictionary of cluster IDs to center coordinates and alive status."""
        return {cluster_id: tuple((2 * (cluster.center/self.width)) - 1)
                for cluster_id, cluster in self.prev_clusters.items()}

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
