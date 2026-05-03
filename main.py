#!/usr/bin/env python3
"""
Graph Navigator - Console Application for Graph Operations
Author: Vara Akuseva
Course: Final Certification Project
Date: 03.05.2026

Features:
- Directed, Undirected, Weighted graphs
- BFS and DFS traversal
- Shortest path (BFS for unweighted, Dijkstra for weighted)
- Factory pattern for graph creation
- JSON persistence
- Full input validation
"""

import json
import os
import heapq
from collections import deque
from typing import Dict, List, Set, Tuple, Optional, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum

# ============================================================================
# GRAPH NODE CLASS
# ============================================================================

@dataclass
class GraphNode:
    """Represents a vertex in the graph"""
    name: str
    data: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}
    
    def to_dict(self) -> dict:
        return {"name": self.name, "data": self.data}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'GraphNode':
        return cls(name=data["name"], data=data.get("data", {}))
    
    def __hash__(self):
        return hash(self.name)
    
    def __eq__(self, other):
        return isinstance(other, GraphNode) and self.name == other.name

# ============================================================================
# ABSTRACT GRAPH CLASS
# ============================================================================

class Graph(ABC):
    """Abstract base class for all graph types"""
    
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.adjacency: Dict[str, Set[str]] = {}
    
    @abstractmethod
    def add_edge(self, from_node: str, to_node: str, weight: float = 1.0) -> bool:
        pass
    
    @abstractmethod
    def remove_edge(self, from_node: str, to_node: str) -> bool:
        pass
    
    def add_node(self, name: str) -> bool:
        if name in self.nodes:
            return False
        self.nodes[name] = GraphNode(name)
        self.adjacency[name] = set()
        return True
    
    def remove_node(self, name: str) -> bool:
        if name not in self.nodes:
            return False
        del self.nodes[name]
        if name in self.adjacency:
            del self.adjacency[name]
        for key in list(self.adjacency.keys()):
            if name in self.adjacency[key]:
                self.adjacency[key].discard(name)
        return True
    
    def get_node(self, name: str) -> Optional[GraphNode]:
        return self.nodes.get(name)
    
    def get_all_nodes(self) -> List[str]:
        return list(self.nodes.keys())
    
    def get_neighbors(self, node: str) -> Set[str]:
        return self.adjacency.get(node, set()).copy()
    
    def get_edge_weight(self, from_node: str, to_node: str) -> float:
        return 1.0
    
    def to_dict(self) -> dict:
        return {
            "type": self.__class__.__name__,
            "nodes": [node.to_dict() for node in self.nodes.values()],
            "edges": self._get_edges_data()
        }
    
    @abstractmethod
    def _get_edges_data(self) -> List[dict]:
        pass

# ============================================================================
# CONCRETE GRAPH TYPES
# ============================================================================

class DirectedGraph(Graph):
    """Directed graph implementation"""
    
    def add_edge(self, from_node: str, to_node: str, weight: float = 1.0) -> bool:
        if from_node not in self.nodes or to_node not in self.nodes:
            return False
        self.adjacency[from_node].add(to_node)
        return True
    
    def remove_edge(self, from_node: str, to_node: str) -> bool:
        if from_node in self.adjacency and to_node in self.adjacency[from_node]:
            self.adjacency[from_node].discard(to_node)
            return True
        return False
    
    def _get_edges_data(self) -> List[dict]:
        edges = []
        for from_node, to_nodes in self.adjacency.items():
            for to_node in to_nodes:
                edges.append({"from": from_node, "to": to_node, "weight": 1})
        return edges
    
    def __str__(self):
        return f"DirectedGraph with {len(self.nodes)} nodes"


class UndirectedGraph(Graph):
    """Undirected graph implementation"""
    
    def add_edge(self, from_node: str, to_node: str, weight: float = 1.0) -> bool:
        if from_node not in self.nodes or to_node not in self.nodes:
            return False
        self.adjacency[from_node].add(to_node)
        self.adjacency[to_node].add(from_node)
        return True
    
    def remove_edge(self, from_node: str, to_node: str) -> bool:
        if from_node in self.adjacency and to_node in self.adjacency[from_node]:
            self.adjacency[from_node].discard(to_node)
            self.adjacency[to_node].discard(from_node)
            return True
        return False
    
    def _get_edges_data(self) -> List[dict]:
        edges = []
        seen = set()
        for from_node, to_nodes in self.adjacency.items():
            for to_node in to_nodes:
                edge_key = tuple(sorted([from_node, to_node]))
                if edge_key not in seen:
                    seen.add(edge_key)
                    edges.append({"from": from_node, "to": to_node, "weight": 1})
        return edges
    
    def __str__(self):
        return f"UndirectedGraph with {len(self.nodes)} nodes"


class WeightedGraph(Graph):
    """Weighted graph implementation"""
    
    def __init__(self):
        super().__init__()
        self.weights: Dict[Tuple[str, str], float] = {}
    
    def add_edge(self, from_node: str, to_node: str, weight: float = 1.0) -> bool:
        if from_node not in self.nodes or to_node not in self.nodes:
            return False
        if weight <= 0:
            return False
        self.adjacency[from_node].add(to_node)
        self.adjacency[to_node].add(from_node)
        self.weights[(from_node, to_node)] = weight
        self.weights[(to_node, from_node)] = weight
        return True
    
    def remove_edge(self, from_node: str, to_node: str) -> bool:
        if from_node in self.adjacency and to_node in self.adjacency[from_node]:
            self.adjacency[from_node].discard(to_node)
            self.adjacency[to_node].discard(from_node)
            if (from_node, to_node) in self.weights:
                del self.weights[(from_node, to_node)]
            if (to_node, from_node) in self.weights:
                del self.weights[(to_node, from_node)]
            return True
        return False
    
    def get_edge_weight(self, from_node: str, to_node: str) -> float:
        return self.weights.get((from_node, to_node), float('inf'))
    
    def _get_edges_data(self) -> List[dict]:
        edges = []
        seen = set()
        for (from_node, to_node), weight in self.weights.items():
            edge_key = tuple(sorted([from_node, to_node]))
            if edge_key not in seen:
                seen.add(edge_key)
                edges.append({"from": from_node, "to": to_node, "weight": weight})
        return edges
    
    def __str__(self):
        return f"WeightedGraph with {len(self.nodes)} nodes"

# ============================================================================
# FACTORY PATTERN
# ============================================================================

class GraphFactory:
    """Factory pattern for creating different graph types"""
    
    GRAPH_TYPES = {
        "directed": DirectedGraph,
        "undirected": UndirectedGraph,
        "weighted": WeightedGraph,
        "1": DirectedGraph,
        "2": UndirectedGraph,
        "3": WeightedGraph
    }
    
    @classmethod
    def create_graph(cls, graph_type: str) -> Graph:
        """Create a graph of specified type"""
        graph_type_lower = graph_type.lower()
        if graph_type_lower not in cls.GRAPH_TYPES:
            raise ValueError(f"Unknown graph type: {graph_type}. Available: directed, undirected, weighted")
        
        return cls.GRAPH_TYPES[graph_type_lower]()
    
    @classmethod
    def get_available_types(cls) -> list:
        return ["directed", "undirected", "weighted"]

# ============================================================================
# GRAPH ALGORITHMS (BFS, DFS, DIJKSTRA)
# ============================================================================

class GraphAlgorithms:
    """Collection of graph algorithms"""
    
    @staticmethod
    def bfs(graph: Graph, start: str, target: Optional[str] = None) -> Tuple[List[str], Dict[str, str]]:
        """
        Breadth-First Search traversal
        Returns: (path to target if found, parent dictionary)
        """
        if start not in graph.get_all_nodes():
            return [], {}
        
        visited: Set[str] = set()
        queue = deque([start])
        parent: Dict[str, str] = {start: None}
        visited.add(start)
        
        while queue:
            current = queue.popleft()
            
            if target and current == target:
                path = GraphAlgorithms._reconstruct_path(parent, start, target)
                return path, parent
            
            for neighbor in graph.get_neighbors(current):
                if neighbor not in visited:
                    visited.add(neighbor)
                    parent[neighbor] = current
                    queue.append(neighbor)
        
        if target:
            return [], parent
        return list(visited), parent
    
    @staticmethod
    def dfs(graph: Graph, start: str, target: Optional[str] = None) -> Tuple[List[str], Dict[str, str]]:
        """
        Depth-First Search traversal (iterative)
        Returns: (path to target if found, parent dictionary)
        """
        if start not in graph.get_all_nodes():
            return [], {}
        
        visited: Set[str] = set()
        stack = [start]
        parent: Dict[str, str] = {start: None}
        
        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                
                if target and current == target:
                    path = GraphAlgorithms._reconstruct_path(parent, start, target)
                    return path, parent
                
                for neighbor in graph.get_neighbors(current):
                    if neighbor not in visited:
                        parent[neighbor] = current
                        stack.append(neighbor)
        
        if target:
            return [], parent
        return list(visited), parent
    
    @staticmethod
    def dijkstra(graph: WeightedGraph, start: str, target: str) -> Tuple[List[str], float]:
        """
        Dijkstra's algorithm for weighted graphs
        Returns: (shortest path, total distance)
        """
        if start not in graph.get_all_nodes() or target not in graph.get_all_nodes():
            return [], float('inf')
        
        distances: Dict[str, float] = {node: float('inf') for node in graph.get_all_nodes()}
        distances[start] = 0
        parent: Dict[str, str] = {start: None}
        pq = [(0, start)]
        visited: Set[str] = set()
        
        while pq:
            current_dist, current = heapq.heappop(pq)
            
            if current in visited:
                continue
            
            if current == target:
                path = GraphAlgorithms._reconstruct_path(parent, start, target)
                return path, distances[target]
            
            visited.add(current)
            
            for neighbor in graph.get_neighbors(current):
                if neighbor in visited:
                    continue
                
                weight = graph.get_edge_weight(current, neighbor)
                new_dist = current_dist + weight
                
                if new_dist < distances[neighbor]:
                    distances[neighbor] = new_dist
                    parent[neighbor] = current
                    heapq.heappush(pq, (new_dist, neighbor))
        
        return [], float('inf')
    
    @staticmethod
    def shortest_path_unweighted(graph: Graph, start: str, target: str) -> Tuple[List[str], int]:
        """Find shortest path in unweighted graph using BFS"""
        path, _ = GraphAlgorithms.bfs(graph, start, target)
        if path:
            return path, len(path) - 1
        return [], -1
    
    @staticmethod
    def _reconstruct_path(parent: Dict[str, str], start: str, target: str) -> List[str]:
        """Reconstruct path from parent dictionary"""
        path = []
        current = target
        while current is not None:
            path.append(current)
            current = parent.get(current)
        path.reverse()
        return path if path[0] == start else []

# ============================================================================
# VALIDATORS
# ============================================================================

class Validators:
    """Input validation methods"""
    
    @staticmethod
    def validate_node_name(name: str) -> Tuple[bool, str]:
        if not name or not name.strip():
            return False, "Node name cannot be empty"
        if len(name) > 50:
            return False, "Node name must be less than 50 characters"
        if not name.replace('_', '').replace('-', '').isalnum():
            return False, "Node name can only contain letters, numbers, underscores, and hyphens"
        return True, ""
    
    @staticmethod
    def validate_weight(weight: str) -> Tuple[bool, float, str]:
        try:
            w = float(weight)
            if w <= 0:
                return False, 0, "Weight must be positive"
            if w > 1000000:
                return False, 0, "Weight is too large (max 1,000,000)"
            return True, w, ""
        except ValueError:
            return False, 0, "Weight must be a number"

# ============================================================================
# JSON HANDLER
# ============================================================================

class JSONHandler:
    DATA_FILE = "graph_data.json"
    
    def __init__(self, filename: str = DATA_FILE):
        self.filename = filename
    
    def save_graph(self, graph: Graph) -> bool:
        """Save graph to JSON file"""
        try:
            data = graph.to_dict()
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print(f"✓ Graph saved to {self.filename}")
            return True
        except Exception as e:
            print(f"✗ Save error: {e}")
            return False
    
    def load_graph(self) -> Optional[Graph]:
        """Load graph from JSON file"""
        if not os.path.exists(self.filename):
            print(f"File {self.filename} not found. Starting empty.")
            return None
        
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                graph_type = data.get("type")
                if graph_type == "DirectedGraph":
                    graph = GraphFactory.create_graph("directed")
                elif graph_type == "UndirectedGraph":
                    graph = GraphFactory.create_graph("undirected")
                elif graph_type == "WeightedGraph":
                    graph = GraphFactory.create_graph("weighted")
                else:
                    print(f"Unknown graph type: {graph_type}")
                    return None
                
                # Add nodes
                for node_data in data.get("nodes", []):
                    graph.add_node(node_data["name"])
                    if node_data.get("data"):
                        graph.nodes[node_data["name"]].data = node_data["data"]
                
                # Add edges
                for edge in data.get("edges", []):
                    from_node = edge["from"]
                    to_node = edge["to"]
                    weight = edge.get("weight", 1.0)
                    graph.add_edge(from_node, to_node, weight)
                
                print(f"✓ Loaded {graph_type} with {len(graph.nodes)} nodes")
                return graph
        except Exception as e:
            print(f"✗ Load error: {e}")
            return None

# ============================================================================
# CONSOLE VIEW
# ============================================================================

class ConsoleView:
    """Handles all console input/output"""
    
    @staticmethod
    def display_main_menu():
        print("\n" + "=" * 60)
        print("GRAPH NAVIGATOR - MAIN MENU")
        print("=" * 60)
        print("1. Create New Graph")
        print("2. Add Node")
        print("3. Add Edge")
        print("4. Remove Node")
        print("5. Remove Edge")
        print("6. View Graph")
        print("7. BFS Traversal")
        print("8. DFS Traversal")
        print("9. Find Shortest Path")
        print("10. View Statistics")
        print("11. Save Graph")
        print("12. Load Graph")
        print("13. Exit")
        print("=" * 60)
    
    @staticmethod
    def display_graph_info(graph: Graph):
        if not graph:
            print("\nNo graph loaded. Create or load a graph first.")
            return
        
        edge_count = 0
        for node in graph.get_all_nodes():
            edge_count += len(graph.get_neighbors(node))
        
        if isinstance(graph, UndirectedGraph):
            edge_count //= 2
        
        print(f"\n📊 Graph Info:")
        print(f"   Type: {graph.__class__.__name__}")
        print(f"   Nodes: {len(graph.get_all_nodes())}")
        print(f"   Edges: {edge_count}")
        if graph.get_all_nodes():
            print(f"   Node list: {', '.join(graph.get_all_nodes()[:10])}")
            if len(graph.get_all_nodes()) > 10:
                print(f"   ... and {len(graph.get_all_nodes()) - 10} more")
    
    @staticmethod
    def display_nodes(nodes: List[str]):
        if not nodes:
            print("\nNo nodes found")
            return
        print("\n📋 Nodes:")
        for i, node in enumerate(nodes, 1):
            print(f"   {i}. {node}")
    
    @staticmethod
    def display_edges(graph: Graph):
        edges = []
        for from_node in graph.get_all_nodes():
            for to_node in graph.get_neighbors(from_node):
                weight = graph.get_edge_weight(from_node, to_node)
                if isinstance(graph, UndirectedGraph):
                    edge_key = tuple(sorted([from_node, to_node]))
                    if edge_key not in [(e[0], e[1]) for e in edges]:
                        edges.append((from_node, to_node, weight))
                else:
                    edges.append((from_node, to_node, weight))
        
        if not edges:
            print("\nNo edges found")
            return
        
        print("\n🔗 Edges:")
        for i, (frm, to, w) in enumerate(edges, 1):
            if w != 1.0:
                print(f"   {i}. {frm} --[{w}]--> {to}")
            else:
                print(f"   {i}. {frm} ---> {to}")
    
    @staticmethod
    def display_path(path: List[str], distance=None):
        if not path:
            print("\n✗ Path not found!")
            return
        
        print("\n✓ Path found:")
        print(f"   {' → '.join(path)}")
        if distance is not None and distance != -1:
            print(f"   Total distance: {distance}")
    
    @staticmethod
    def display_traversal(traversal: List[str]):
        if not traversal:
            print("\n✗ Start node not found!")
            return
        print(f"\n✓ Traversal order: {' → '.join(traversal)}")
    
    @staticmethod
    def display_statistics(stats: dict):
        print("\n" + "=" * 50)
        print("GRAPH STATISTICS")
        print("=" * 50)
        for key, value in stats.items():
            print(f"   {key}: {value}")
        print("=" * 50)
    
    @staticmethod
    def show_message(message: str, is_error: bool = False):
        prefix = "✗ ERROR:" if is_error else "✓ INFO:"
        print(f"\n{prefix} {message}")
    
    @staticmethod
    def get_user_input(prompt: str) -> str:
        return input(prompt).strip()
    
    @staticmethod
    def get_yes_no(prompt: str) -> bool:
        response = input(f"{prompt} (y/n): ").lower().strip()
        return response == 'y' or response == 'yes'
    
    @staticmethod
    def get_graph_type() -> str:
        print("\nSelect graph type:")
        print("   1. Directed Graph")
        print("   2. Undirected Graph")
        print("   3. Weighted Graph")
        choice = input("Choice (1-3): ").strip()
        type_map = {"1": "directed", "2": "undirected", "3": "weighted"}
        return type_map.get(choice, "undirected")
    
    @staticmethod
    def get_node_name() -> str:
        return input("Node name: ").strip()
    
    @staticmethod
    def get_edge_input() -> Tuple[str, str, str]:
        from_node = input("From node: ").strip()
        to_node = input("To node: ").strip()
        weight = input("Weight (optional, default=1): ").strip()
        return from_node, to_node, weight

# ============================================================================
# CONTROLLER
# ============================================================================

class GraphController:
    def __init__(self):
        self.graph: Optional[Graph] = None
        self.view = ConsoleView()
        self.json_handler = JSONHandler()
        self.validators = Validators()
        self.is_running = True
    
    def run(self):
        """Main application loop"""
        while self.is_running:
            self.view.display_main_menu()
            choice = self.view.get_user_input("\nEnter choice (1-13): ")
            
            if choice == "1":
                self.create_graph()
            elif choice == "2":
                self.add_node()
            elif choice == "3":
                self.add_edge()
            elif choice == "4":
                self.remove_node()
            elif choice == "5":
                self.remove_edge()
            elif choice == "6":
                self.view_graph()
            elif choice == "7":
                self.bfs_traversal()
            elif choice == "8":
                self.dfs_traversal()
            elif choice == "9":
                self.shortest_path()
            elif choice == "10":
                self.show_statistics()
            elif choice == "11":
                self.save_graph()
            elif choice == "12":
                self.load_graph()
            elif choice == "13":
                self.save_and_exit()
            else:
                self.view.show_message("Invalid choice. Please enter 1-13", is_error=True)
    
    def create_graph(self):
        """Create a new graph"""
        graph_type = self.view.get_graph_type()
        try:
            self.graph = GraphFactory.create_graph(graph_type)
            self.view.show_message(f"Created new {graph_type} graph")
        except ValueError as e:
            self.view.show_message(str(e), is_error=True)
    
    def add_node(self):
        """Add a new node to the graph"""
        if not self._check_graph_exists():
            return
        
        name = self.view.get_node_name()
        valid, error = self.validators.validate_node_name(name)
        if not valid:
            self.view.show_message(error, is_error=True)
            return
        
        if self.graph.add_node(name):
            self.view.show_message(f"Node '{name}' added successfully")
        else:
            self.view.show_message(f"Node '{name}' already exists", is_error=True)
    
    def add_edge(self):
        """Add a new edge to the graph"""
        if not self._check_graph_exists():
            return
        
        from_node, to_node, weight_str = self.view.get_edge_input()
        
        # Check nodes exist
        if from_node not in self.graph.get_all_nodes():
            self.view.show_message(f"Node '{from_node}' not found", is_error=True)
            return
        if to_node not in self.graph.get_all_nodes():
            self.view.show_message(f"Node '{to_node}' not found", is_error=True)
            return
        
        # Validate weight
        weight = 1.0
        if weight_str:
            valid, w, error = self.validators.validate_weight(weight_str)
            if not valid:
                self.view.show_message(error, is_error=True)
                return
            weight = w
        
        if self.graph.add_edge(from_node, to_node, weight):
            if weight != 1.0:
                self.view.show_message(f"Edge added: {from_node} -[{weight}]-> {to_node}")
            else:
                self.view.show_message(f"Edge added: {from_node} -> {to_node}")
        else:
            self.view.show_message("Failed to add edge", is_error=True)
    
    def remove_node(self):
        """Remove a node from the graph"""
        if not self._check_graph_exists():
            return
        
        name = self.view.get_node_name()
        if self.graph.remove_node(name):
            self.view.show_message(f"Node '{name}' removed successfully")
        else:
            self.view.show_message(f"Node '{name}' not found", is_error=True)
    
    def remove_edge(self):
        """Remove an edge from the graph"""
        if not self._check_graph_exists():
            return
        
        from_node = self.view.get_user_input("From node: ")
        to_node = self.view.get_user_input("To node: ")
        
        if self.graph.remove_edge(from_node, to_node):
            self.view.show_message(f"Edge removed: {from_node} -> {to_node}")
        else:
            self.view.show_message("Edge not found", is_error=True)
    
    def view_graph(self):
        """Display graph information"""
        if not self._check_graph_exists():
            return
        
        self.view.display_graph_info(self.graph)
        self.view.display_nodes(self.graph.get_all_nodes())
        self.view.display_edges(self.graph)
    
    def bfs_traversal(self):
        """BFS traversal of the graph"""
        if not self._check_graph_exists():
            return
        
        start = self.view.get_user_input("Start node: ")
        target = self.view.get_user_input("Target node (optional, press Enter to skip): ")
        
        if target:
            path, _ = GraphAlgorithms.bfs(self.graph, start, target)
            self.view.display_path(path)
        else:
            traversal, _ = GraphAlgorithms.bfs(self.graph, start)
            self.view.display_traversal(traversal)
    
    def dfs_traversal(self):
        """DFS traversal of the graph"""
        if not self._check_graph_exists():
            return
        
        start = self.view.get_user_input("Start node: ")
        target = self.view.get_user_input("Target node (optional): ")
        
        if target:
            path, _ = GraphAlgorithms.dfs(self.graph, start, target)
            self.view.display_path(path)
        else:
            traversal, _ = GraphAlgorithms.dfs(self.graph, start)
            self.view.display_traversal(traversal)
    
    def shortest_path(self):
        """Find shortest path between two nodes"""
        if not self._check_graph_exists():
            return
        
        start = self.view.get_user_input("Start node: ")
        target = self.view.get_user_input("Target node: ")
        
        if start not in self.graph.get_all_nodes():
            self.view.show_message(f"Node '{start}' not found", is_error=True)
            return
        if target not in self.graph.get_all_nodes():
            self.view.show_message(f"Node '{target}' not found", is_error=True)
            return
        
        if isinstance(self.graph, WeightedGraph):
            path, distance = GraphAlgorithms.dijkstra(self.graph, start, target)
            self.view.display_path(path, distance)
        else:
            path, length = GraphAlgorithms.shortest_path_unweighted(self.graph, start, target)
            self.view.display_path(path, length)
    
    def show_statistics(self):
        """Display graph statistics"""
        if not self._check_graph_exists():
            return
        
        edge_count = 0
        for node in self.graph.get_all_nodes():
            edge_count += len(self.graph.get_neighbors(node))
        
        if isinstance(self.graph, UndirectedGraph):
            edge_count //= 2
        
        stats = {
            "Graph Type": self.graph.__class__.__name__,
            "Number of Nodes": len(self.graph.get_all_nodes()),
            "Number of Edges": edge_count
        }
        
        self.view.display_statistics(stats)
    
    def save_graph(self):
        """Save graph to JSON file"""
        if not self._check_graph_exists():
            return
        
        if self.json_handler.save_graph(self.graph):
            self.view.show_message("Graph saved successfully")
    
    def load_graph(self):
        """Load graph from JSON file"""
        loaded = self.json_handler.load_graph()
        if loaded:
            self.graph = loaded
            self.view.show_message("Graph loaded successfully")
    
    def save_and_exit(self):
        """Save graph and exit"""
        if self.graph and self.view.get_yes_no("Save graph before exit?"):
            self.json_handler.save_graph(self.graph)
        self.view.show_message("Goodbye!")
        self.is_running = False
    
    def _check_graph_exists(self) -> bool:
        """Check if graph exists, show error if not"""
        if not self.graph:
            self.view.show_message("No graph loaded. Create or load a graph first (option 1 or 12)", is_error=True)
            return False
        return True

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("\n" + "=" * 60)
    print("GRAPH NAVIGATOR v1.0")
    print("=" * 60)
    print("Features:")
    print("  ✓ Directed, Undirected, Weighted graphs")
    print("  ✓ BFS and DFS traversal")
    print("  ✓ Shortest path (BFS for unweighted, Dijkstra for weighted)")
    print("  ✓ Factory pattern for graph creation")
    print("  ✓ JSON persistence")
    print("  ✓ Full input validation")
    print("=" * 60)
    
    app = GraphController()
    app.run()

if __name__ == "__main__":
    main()
    #!/usr/bin/env python3
"""
Unit tests for Graph Navigator
Run with: python test.py
"""

import unittest
import os
import tempfile
from main import (
    DirectedGraph, UndirectedGraph, WeightedGraph,
    GraphAlgorithms, GraphFactory, Validators, JSONHandler
)

class TestGraphCreation(unittest.TestCase):
    """Tests for graph creation"""
    
    def setUp(self):
        self.directed = DirectedGraph()
        self.undirected = UndirectedGraph()
        self.weighted = WeightedGraph()
    
    def test_add_node_positive(self):
        result = self.directed.add_node("A")
        self.assertTrue(result)
        self.assertIn("A", self.directed.get_all_nodes())
    
    def test_add_duplicate_node_negative(self):
        self.directed.add_node("A")
        result = self.directed.add_node("A")
        self.assertFalse(result)
    
    def test_remove_node_positive(self):
        self.directed.add_node("A")
        result = self.directed.remove_node("A")
        self.assertTrue(result)
        self.assertNotIn("A", self.directed.get_all_nodes())
    
    def test_remove_nonexistent_node_negative(self):
        result = self.directed.remove_node("Z")
        self.assertFalse(result)

class TestEdges(unittest.TestCase):
    """Tests for edge operations"""
    
    def setUp(self):
        self.directed = DirectedGraph()
        self.undirected = UndirectedGraph()
        self.weighted = WeightedGraph()
        
        for g in [self.directed, self.undirected, self.weighted]:
            g.add_node("A")
            g.add_node("B")
            g.add_node("C")
    
    def test_add_edge_directed_positive(self):
        result = self.directed.add_edge("A", "B")
        self.assertTrue(result)
        self.assertIn("B", self.directed.get_neighbors("A"))
        self.assertNotIn("A", self.directed.get_neighbors("B"))
    
    def test_add_edge_undirected_positive(self):
        result = self.undirected.add_edge("A", "B")
        self.assertTrue(result)
        self.assertIn("B", self.undirected.get_neighbors("A"))
        self.assertIn("A", self.undirected.get_neighbors("B"))
    
    def test_add_edge_weighted_positive(self):
        result = self.weighted.add_edge("A", "B", 5.0)
        self.assertTrue(result)
        self.assertEqual(self.weighted.get_edge_weight("A", "B"), 5.0)
    
    def test_add_edge_with_invalid_weight_negative(self):
        result = self.weighted.add_edge("A", "B", -1.0)
        self.assertFalse(result)
    
    def test_add_edge_nonexistent_nodes_negative(self):
        result = self.directed.add_edge("A", "Z")
        self.assertFalse(result)
    
    def test_remove_edge_positive(self):
        self.directed.add_edge("A", "B")
        result = self.directed.remove_edge("A", "B")
        self.assertTrue(result)
        self.assertNotIn("B", self.directed.get_neighbors("A"))

class TestAlgorithms(unittest.TestCase):
    """Tests for BFS, DFS, and Dijkstra algorithms"""
    
    def setUp(self):
        self.graph = DirectedGraph()
        self.graph.add_node("A")
        self.graph.add_node("B")
        self.graph.add_node("C")
        self.graph.add_node("D")
        self.graph.add_edge("A", "B")
        self.graph.add_edge("B", "C")
        self.graph.add_edge("C", "D")
    
    def test_bfs_path_found_positive(self):
        path, _ = GraphAlgorithms.bfs(self.graph, "A", "D")
        self.assertEqual(path, ["A", "B", "C", "D"])
    
    def test_bfs_path_not_found_negative(self):
        path, _ = GraphAlgorithms.bfs(self.graph, "A", "Z")
        self.assertEqual(path, [])
    
    def test_bfs_traversal(self):
        traversal, _ = GraphAlgorithms.bfs(self.graph, "A")
        self.assertEqual(traversal, ["A", "B", "C", "D"])
    
    def test_dfs_path_found_positive(self):
        path, _ = GraphAlgorithms.dfs(self.graph, "A", "D")
        self.assertEqual(path[-1], "D")
    
    def test_dfs_traversal(self):
        traversal, _ = GraphAlgorithms.dfs(self.graph, "A")
        self.assertEqual(len(traversal), 4)
    
    def test_shortest_path_unweighted(self):
        path, length = GraphAlgorithms.shortest_path_unweighted(self.graph, "A", "D")
        self.assertEqual(length, 3)

class TestWeightedAlgorithms(unittest.TestCase):
    """Tests for weighted graph algorithms"""
    
    def setUp(self):
        self.graph = WeightedGraph()
        self.graph.add_node("A")
        self.graph.add_node("B")
        self.graph.add_node("C")
        self.graph.add_node