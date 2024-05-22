from .nodes import NODE_CLASS_MAPPINGS as nodes_mappings

NODE_CLASS_MAPPINGS = {}
for mappings in (
        nodes_mappings, 
    ):
    for mapping in mappings:
        NODE_CLASS_MAPPINGS[mapping] = mappings[mapping]

__all__ = ["NODE_CLASS_MAPPINGS"]

VERSION = "0.1"