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
        self.life = 1000  # initial life value

    def update(self, center):
        self.center = center

    def kill(self):
        self.alive = False

    def revive(self):
        """Revive the cluster by marking it as alive and resetting its life."""
        self.alive = True
        self.life = 60

class ClusterTracker:
    def __init__(self, radius):
        """
        Initialize the cluster tracker.

        Args:
            radius (float): The radius to consider points as part of a cluster.
        """
        self.radius = radius
        self.prev_clusters = {}  # Mapping from our unique cluster id to Cluster objects.
        self.next_cluster_id = 0  # Incremented for every new cluster.

    def set_radius(self, radius):
        self.radius = radius

    def find_clusters(self, points):
        """
        Identify clusters using DBSCAN.

        Returns:
            dict: Dictionary mapping DBSCAN label to list of points.
        """
        if not points:
            return {}
        points_array = np.array(points)
        db = DBSCAN(eps=self.radius, min_samples=2).fit(points_array)
        labels = db.labels_

        clusters = {}
        for point, label in zip(points, labels):
            # Ignore noise points (label == -1)
            if label == -1:
                continue
            clusters.setdefault(label, []).append(point)
        return clusters

    def match_clusters(self, new_clusters):
        """
        Match new clusters from DBSCAN to existing Cluster objects.
        If an existing cluster's center is within the radius of a new cluster's centroid,
        update that cluster's center, revive it (resetting its life), and maintain its ID.
        Otherwise, mark it as dead.
        Any new cluster that doesn't match an existing one is created with a new unique id.

        Args:
            new_clusters (dict): Mapping from DBSCAN label to list of points.

        Returns:
            dict: Updated mapping from our cluster id to Cluster objects.
        """
        updated_clusters = {}

        # Calculate centroids for existing clusters.
        prev_ids = list(self.prev_clusters.keys())
        prev_centroids = [np.array(self.prev_clusters[cid].center) for cid in prev_ids]

        # Calculate centroids for new clusters.
        new_labels = list(new_clusters.keys())
        new_centroids = [np.mean(np.array(new_clusters[label]), axis=0) for label in new_labels]

        used_new = set()
        if prev_ids and new_labels:
            # Compute the distance matrix between previous and new centroids.
            distances = cdist(np.array(prev_centroids), np.array(new_centroids))
            # For each existing cluster, find the closest new cluster.
            for i, cid in enumerate(prev_ids):
                closest_idx = np.argmin(distances[i])
                if distances[i][closest_idx] <= self.radius:
                    new_label = new_labels[closest_idx]
                    # Only update if this new cluster hasn't been used already.
                    if new_label not in used_new:
                        self.prev_clusters[cid].update(new_centroids[closest_idx])
                        # Revive the cluster (set alive and reset life) if it was previously dead.
                        self.prev_clusters[cid].revive()
                        updated_clusters[cid] = self.prev_clusters[cid]
                        used_new.add(new_label)
                    else:
                        # If this new cluster has already been used for matching, mark this one as dead.
                        self.prev_clusters[cid].kill()
                        updated_clusters[cid] = self.prev_clusters[cid]
                else:
                    # No close new cluster found; mark the cluster as dead.
                    self.prev_clusters[cid].kill()
                    updated_clusters[cid] = self.prev_clusters[cid]

            # Remove matched new clusters from new_clusters.
            for label in used_new:
                new_clusters.pop(label)

        # Create new Cluster objects for any unmatched new clusters.
        for label, pts in new_clusters.items():
            centroid = np.mean(np.array(pts), axis=0)
            new_cluster = Cluster(self.next_cluster_id, centroid)
            updated_clusters[new_cluster.id] = new_cluster
            self.next_cluster_id += 1

        return updated_clusters

    def update(self, points):
        """
        Update clusters based on the current set of points.
        Any cluster that has reached a life of zero will be removed permanently.

        Args:
            points (list): List of (x, y) coordinates.

        Returns:
            dict: Mapping from our cluster id to Cluster objects.
        """
        new_clusters = self.find_clusters(points)
        if self.prev_clusters:
            self.prev_clusters = self.match_clusters(new_clusters)
        else:
            clusters_dict = {}
            for label, pts in new_clusters.items():
                centroid = np.mean(np.array(pts), axis=0)
                cluster_obj = Cluster(self.next_cluster_id, centroid)
                clusters_dict[cluster_obj.id] = cluster_obj
                self.next_cluster_id += 1
            self.prev_clusters = clusters_dict

        # Remove clusters that have been marked as dead and have expired (life <= 0).
        self.prev_clusters = {cid: cluster for cid, cluster in self.prev_clusters.items() if cluster.life > 0}

    def decrease_life(self):
        """
        Decrease the life of clusters that are not alive.
        This should be called periodically from external code.
        """
        for cluster in self.prev_clusters.values():
            if not cluster.alive:
                cluster.life -= 1

    def get_cluster_centers_dict(self):
        """
        Returns a dictionary mapping cluster IDs to their center coordinates and their alive status.

        Returns:
            dict: {ID: ((center_x, center_y), alive)}
        """
        return {cluster_id: tuple(cluster.center) for cluster_id, cluster in self.prev_clusters.items()}

  # Create the OSC client
osc_address = "192.168.1.146"
osc_port = 7000

osc_client = udp_client.SimpleUDPClient(osc_address, osc_port)

# Example testing
points_time1 = [(0.1, 0.2), (0.2, 0.2), (0.8, 0.9), (0.7, 0.9)]
points_time2 = [(1.5, 2.5), (2.5, 2.5), (3.5, 3.5), (10.5, 10.5), (11.5, 11.5), (49.5, 49.5), (50, 50)]
points_time3 = [(49.7, 49.7), (50.3, 50.3)]
points_time4 = [(49.7, 49.7), (50.3, 50.3), (1, 2), (2, 2), (3, 3), (2.2, 2.2)]

tracker = ClusterTracker(radius=0.3)

print("Time 1 Clusters:")
clusters1 = tracker.update([])
tracker.decrease_life()
print(tracker.get_cluster_centers_dict())
osc_client.send_message("/clusters", json.dumps(tracker.get_cluster_centers_dict()))

# print("\nTime 2 Clusters:")
# clusters2 = tracker.update(points_time2)
# tracker.decrease_life()
# print(tracker.get_cluster_centers_dict())

# print("\nTime 3 Clusters:")
# clusters3 = tracker.update(points_time3)
# tracker.decrease_life()
# print(tracker.get_cluster_centers_dict())

# print("\nTime 4 Clusters:")
# clusters4 = tracker.update(points_time4)
# tracker.decrease_life()
# print(tracker.get_cluster_centers_dict())
