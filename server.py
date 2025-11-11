from fastapi import FastAPI, File, UploadFile
from typing_extensions import Annotated
import uvicorn
from utils import *
from dijkstra import dijkstra

# create FastAPI app
app = FastAPI()

# global variable for active graph
active_graph = None

@app.get("/")
async def root():
    return {"message": "Welcome to the Shortest Path Solver!"}


@app.post("/upload_graph_json/")
async def create_upload_file(file: UploadFile):
    """
    Upload a JSON file containing graph connectivity and distance information.
    
    Args:
        file: The uploaded file
        
    Returns:
        Success message with filename or error message
    """
    global active_graph
    
    # Check if the file is a JSON file
    if not file.filename.endswith('.json'):
        return {"Upload Error": "Invalid file type"}
    
    # Create graph from the JSON file
    try:
        active_graph = create_graph_from_json(file)
        return {"Upload Success": file.filename}
    except Exception as e:
        return {"Upload Error": f"Failed to parse JSON file: {str(e)}"}


@app.get("/solve_shortest_path/start_node_id={start_node_id}&end_node_id={end_node_id}")
async def get_shortest_path(start_node_id: str, end_node_id: str):
    """
    Solve the shortest path problem for the given graph.
    
    Args:
        start_node_id: The starting node ID
        end_node_id: The ending node ID
        
    Returns:
        Dictionary containing the shortest path and total distance
    """
    global active_graph
    
    # Check if a valid graph has been uploaded
    if active_graph is None:
        return {"Solver Error": "No active graph, please upload a graph first."}
    
    # Check if start and end node IDs exist in the graph
    if start_node_id not in active_graph.nodes:
        return {"Solver Error": "Invalid start or end node ID."}
    
    if end_node_id not in active_graph.nodes:
        return {"Solver Error": "Invalid start or end node ID."}
    
    # Get the start and end nodes
    start_node = active_graph.nodes[start_node_id]
    end_node = active_graph.nodes[end_node_id]
    
    # Run Dijkstra's algorithm
    dijkstra(active_graph, start_node)
    
    # Check if a path exists (end_node.dist will be infinity if no path exists)
    if end_node.dist == np.inf:
        return {
            "shortest_path": None,
            "total_distance": None
        }
    
    # Reconstruct the shortest path by backtracking from end_node to start_node
    path = []
    current_node = end_node
    
    while current_node is not None:
        path.append(current_node.id)
        current_node = current_node.prev
    
    # Reverse the path to get it from start to end
    path.reverse()
    
    # Return the result
    return {
        "shortest_path": path,
        "total_distance": float(end_node.dist)
    }


if __name__ == "__main__":
    print("Server is running at http://localhost:8080")
    uvicorn.run(app, host="0.0.0.0", port=8080)
