"""
Data Mapper for FIRE Agent.
Refactors the "wiring" logic out of orchestrator.py.
Translates calculation results into arguments for the roadmap generator.
"""
from typing import Dict, Any

def build_roadmap_context(projection_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build the context arguments for generating the FIRE roadmap.
    
    Args:
        projection_data: The dictionary returned by calculate_fire_projections.
        
    Returns:
        A dictionary of arguments to pass to generate_fire_roadmap.
    """
    # Currently, generate_fire_roadmap just takes the data dict as 'data'.
    # This layer exists to decouple the orchestrator from the specific args of the generator,
    # and to allow future expansion (e.g. injecting user preferences, date overrides, etc).
    
    return {
        "data": projection_data
    }
