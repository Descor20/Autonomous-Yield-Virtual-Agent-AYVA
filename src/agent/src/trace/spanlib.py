import contextlib
import contextvars
import time
import uuid



SPANS: list[dict] = []                                   # notre « backend » : tous les spans terminés
_SPAN_COURANT = contextvars.ContextVar("span_courant", default=None)


@contextlib.contextmanager
def span(nom: str, type: str = "span", **attributs):
    parent = _SPAN_COURANT.get()
    s = {
        "id": uuid.uuid4().hex[:8],
        "trace_id": parent["trace_id"] if (parent != None and parent["trace_id"] != None) else uuid.uuid4().hex[:8],
        "parent_id": parent["id"] if (parent != None and parent["id"] != None) else None,
        "nom": nom,
        "type": type,
        "attributs": attributs,
        "debut": time.time(),
        "fin": None,
        "erreur": None
    }

    try :
        _SPAN_COURANT.set(s)
        #_SPAN_COURANT.reset()
    except Exception as e :
        s["erreur"] = str(e)

    try :
        yield s
    except Exception as e :
        s["erreur"] = str(e)

    s["fin"] = time.time()
    SPANS.append(s)