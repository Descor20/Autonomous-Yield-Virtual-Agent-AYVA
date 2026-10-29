def new_tool(fonction, description: str, proprietes: dict, requis: list[str], *,
          lecture_seule: bool = True, destructif: bool = False, non_fiable: bool = False) -> dict:
    
    "Un outil = schéma pour l'API Claude + fonction Python + annotations (façon MCP)."
    return {"schema": {"name": fonction.__name__, "description": description,
                       "input_schema": {"type": "object", "properties": proprietes, "required": requis}},
            "fonction": fonction, "lecture_seule": lecture_seule, "destructif": destructif, "non_fiable": non_fiable}