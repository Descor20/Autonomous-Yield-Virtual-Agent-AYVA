import asyncio
import time

from .spanlib import SPANS, span


async def test_span() :
    SPANS.clear()
    with span("racine", type="agent") as a:
        with span("enfant", type="tool", entree="x"):
            time.sleep(0.01)
        try:
            with span("en_erreur", type="tool"):
                raise ValueError("boum")
        except ValueError:
            pass

    assert [s["nom"] for s in SPANS] == ["enfant", "en_erreur", "racine"], "ordre de fermeture des spans"
    assert SPANS[0]["parent_id"] == a["id"] and SPANS[0]["trace_id"] == a["trace_id"], "parent / trace de l'enfant"
    assert SPANS[2]["parent_id"] is None and "boum" in (SPANS[1]["erreur"] or ""), "racine sans parent, erreur notée"
    assert SPANS[0]["fin"] - SPANS[0]["debut"] >= 0.01


    async def _test_async():
        with span("parent_async") as p:
            async def tache(i):
                with span(f"tache_{i}"):
                    await asyncio.sleep(0.01)
            await asyncio.gather(tache(1), tache(2))
        return p

    p = await _test_async()
    assert all(s["parent_id"] == p["id"] for s in SPANS if s["nom"].startswith("tache_")), "parents en asyncio"
    SPANS.clear()
    print("✓ traceur OK")