import math
import time
import numpy as np
import random
random.seed(10)
    
class AntColony:
    def __init__(self, points, n_ants, n_iterations, decay_rate=0.5, alpha=1, beta=2, rho=0.1):
        self.distances = self.generate_distance_matrix(points)
        self.n_ants = n_ants
        self.n_iterations = n_iterations
        self.decay_rate = decay_rate
        self.alpha = alpha
        self.beta = beta
        self.rho = rho
        self.n_cities = len(self.distances)
        self.pheromone = np.ones((self.n_cities, self.n_cities))
        self.global_best_path = None
        self.global_best_distance = np.inf
        self.stop = False
        self.start_time = 0
        self.points = points

    def run(self):
        self.start_time = time.time()
        for i in range(self.n_iterations):
            if self.stop:
                break
            all_paths = self.generate_solutions()
            if i == self.n_iterations//3*2:
                all_paths.append(self.untagle(self.global_best_path))
            self.update_pheromone(all_paths)
            current_best_path, current_best_distance = self.get_best_path(all_paths)
            if current_best_distance < self.global_best_distance:
                self.global_best_path = current_best_path
                self.global_best_distance = current_best_distance
                print(f"Iteration {i+1}: Global Best Distance: {self.global_best_distance} [{time.time()-self.start_time} s]")
                # time.sleep(0.5)
            self.pheromone *= self.decay_rate
        
        print(f"finished at iteration {i+1}: Global Best Distance: {self.global_best_distance} [{time.time()-self.start_time} s]")
        print("best path", [self.points[i] for i in self.global_best_path])
                # time.sleep(0.5)
        self.global_best_path = self.untagle(self.global_best_path)
        print(f"untagnled [{time.time()-self.start_time} s]")
        
    def is_intersection(self, p1, p2, p3, p4):
        """Check if line segment (p1,p2) intersects (p3,p4)."""
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])

        return ccw(p1, p3, p4) != ccw(p2, p3, p4) and ccw(p1, p2, p3) != ccw(p1, p2, p4)

    def untagle(self, inp_path):
        intersecting_segments = []
        path = inp_path.copy()

        # Check for intersections between line segments
        while True:
            intersecting_segments = []
            for i in range(self.n_cities - 2):
                for j in range(i + 2, self.n_cities - 1):
                    if self.is_intersection(self.points[path[i]], self.points[path[i+1]], self.points[path[j]], self.points[path[j+1]]):
                        intersecting_segments.append((i, i+1, j, j+1))
            print(intersecting_segments)
            if len(intersecting_segments):
                i1, i2, j1, j2 = intersecting_segments[0]
                path[i2:j1+1] = path[i2:j1+1][::-1]
            else:
                break
        return path
            

    def generate_solutions(self):
        all_paths = []
        for _ in range(self.n_ants):
            path = self.generate_path()
            all_paths.append(path)
        return all_paths

    def generate_path(self):
        path = [0]  # Start from city 0
        unvisited_cities = set(range(1, self.n_cities))
        while unvisited_cities:
            probabilities = self.calculate_probabilities(path[-1], unvisited_cities)
            next_city = np.random.choice(list(unvisited_cities), p=probabilities)
            path.append(next_city)
            unvisited_cities.remove(next_city)
        # path.append(0)  # Return to starting city
        return path

    def calculate_probabilities(self, current_city, unvisited_cities):
        probabilities = []
        total_pheromone = 0
        for city in unvisited_cities:
            pheromone = self.pheromone[current_city][city]
            distance = self.distances[current_city][city]
            total_pheromone += (pheromone ** self.alpha) * ((1 / distance) ** self.beta)
        for city in unvisited_cities:
            pheromone = self.pheromone[current_city][city]
            distance = self.distances[current_city][city]
            probability = ((pheromone ** self.alpha) * ((1 / distance) ** self.beta)) / total_pheromone
            probabilities.append(probability)
        return probabilities

    def update_pheromone(self, all_paths):
        for path in all_paths:
            path_distance = self.calculate_distance(path)
            for i in range(len(path) - 1):
                current_city, next_city = path[i], path[i + 1]
                self.pheromone[current_city][next_city] += 1 / path_distance

    def calculate_distance(self, path):
        distance = 0
        for i in range(len(path) - 1):
            current_city, next_city = path[i], path[i + 1]
            distance += self.distances[current_city][next_city]
        return distance

    def get_best_path(self, all_paths):
        best_path = None
        best_distance = np.inf
        for path in all_paths:
            distance = self.calculate_distance(path)
            if distance < best_distance:
                best_path = path
                best_distance = distance
        return best_path, best_distance
    
    def generate_distance_matrix(self, points):
        num_points = len(points)
        distance_matrix = [[0] * num_points for _ in range(num_points)]
        for i in range(num_points):
            for j in range(num_points):
                if i != j:
                    distance_matrix[i][j] = calculate_distance(points[i], points[j])
        return distance_matrix


def calculate_distance(point1, point2):
    return abs(point2[0] - point1[0]) + abs(point2[1] - point1[1])


# Define distances between cities (replace this with your actual distance matrix)
def generate_random_points(num_points, min_coord, max_coord):
    points = []
    for _ in range(num_points):
        x = random.uniform(min_coord, max_coord)
        y = random.uniform(min_coord, max_coord)
        points.append((x, y))
    return points

# # Example usage:
# num_points = 10
# min_coord = 0
# max_coord = 100
# random.seed = 0
# # random_points = generate_random_points(num_points, min_coord, max_coord)
# random_points = [(1, 0), (2, 0), (7, 0), (9, 0), (0, 1), (4, 1), (7, 1), (8, 1), (2, 2), (3, 2), (5, 2), (6, 2), (9, 2), (3, 3), (4, 3), (7, 3), (9, 3), (1, 4), (2, 4), (5, 4), (6, 4), (9, 4), (0, 5), (3, 5), (4, 5), (5, 5), (7, 5), (8, 5), (0, 6), (5, 6), (6, 6), (8, 6), (1, 7), (3, 7), (4, 7), (6, 7), (8, 7), (1, 8), (2, 8), (4, 8), (6, 8), (7, 8), (9, 8), (0, 9), (2, 9), (3, 9), (7, 9), (8, 9), (0, 10), (1, 10), (3, 10), (5, 10), (6, 10), (8, 10), (9, 10), (0, 11), (3, 11), (4, 11), (6, 11), (7, 11), (8, 11), (9, 11), (1, 12), (2, 12), (3, 12), (9, 12), (0, 13), (1, 13), (5, 13)]
# distances = generate_distance_matrix(random_points)
# print(random_points)
# print(distances)

# n_ants = 50
# n_iterations = 100
# decay_rate = 0.5
# alpha = 1
# beta = 2
# rho = 0.1

# aco = AntColony(distances, n_ants, n_iterations, decay_rate, alpha, beta, rho)
# aco.run()
# print("Global Best Path:", [random_points[i] for i in aco.global_best_path])
# print("Global Best Distance:", aco.global_best_distance)
