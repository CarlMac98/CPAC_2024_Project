import numpy as np
from sklearn.cluster import DBSCAN
from scipy.spatial.distance import cdist

class ClusterTracker:
    def __init__(self, radius):
        """
        Initialize the cluster tracker.

        Args:
            radius (float): The radius to consider points as part of a cluster.
        """
        self.radius = radius
        self.prev_clusters = {}

    def set_radius(self, radius):
        self.radius = radius

    def find_clusters(self, points):
        """
        Identify clusters using DBSCAN.
        """
        points_array = np.array(points)
        db = DBSCAN(eps=self.radius, min_samples=2).fit(points_array)
        labels = db.labels_

        clusters = {}
        for point, label in zip(points, labels):
            if label == -1:
                continue
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(point)
        return clusters

    def match_clusters(self, prev_clusters, new_clusters):
        """
        Match new clusters to previous clusters to track movement.

        Args:
            prev_clusters (dict): Previous clusters.
            new_clusters (dict): Current clusters.

        Returns:
            dict: Updated clusters with their statuses.
        """
        updated_clusters = {}
        prev_centroids = {label: np.mean(points, axis=0) for label, points in prev_clusters.items()}
        new_centroids = {label: np.mean(points, axis=0) for label, points in new_clusters.items()}

        # Create a distance matrix between old and new centroids
        prev_labels = list(prev_centroids.keys())
        new_labels = list(new_centroids.keys())

        if prev_labels and new_labels:
            distances = cdist(
                np.array([prev_centroids[label] for label in prev_labels]),
                np.array([new_centroids[label] for label in new_labels]),
            )

            # Match clusters based on nearest centroids
            for i, prev_label in enumerate(prev_labels):
                closest_new_idx = np.argmin(distances[i])
                if distances[i][closest_new_idx] <= self.radius:
                    new_label = new_labels[closest_new_idx]
                    updated_clusters[prev_label] = new_clusters[new_label]
                    new_clusters.pop(new_label)

        # Any unmatched new clusters are considered new
        for label, points in new_clusters.items():
            updated_clusters[label] = points

        return updated_clusters

    def update(self, points):
        """
        Update the clusters based on the current points.

        Args:
            points (list): List of (x, y) coordinates.

        Returns:
            dict: Current clusters with their statuses.
        """
        new_clusters = self.find_clusters(points)
        if self.prev_clusters:
            self.prev_clusters = self.match_clusters(self.prev_clusters, new_clusters)
        else:
            self.prev_clusters = new_clusters
        return self.prev_clusters


# # Example Usage
# points_time1 = [(1, 2), (2, 2), (3, 3), (10, 10), (11, 11), (50, 50)]
# points_time2 = [(1.5, 2.5), (2.5, 2.5), (3.5, 3.5), (10.5, 10.5), (11.5, 11.5), (49.5, 49.5)]
# points_time3 = [(1.8, 2.8), (2.8, 2.8), (10.8, 10.8), (11.8, 11.8)]

# tracker = ClusterTracker(radius=2.0)

# # Update clusters over time
# print("Time 1 Clusters:")
# print(tracker.update(points_time1))
# print("\nTime 2 Clusters:")
# print(tracker.update(points_time2))
# print("\nTime 3 Clusters:")
# print(tracker.update(points_time3))

