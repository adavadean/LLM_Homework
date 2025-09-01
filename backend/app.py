import json
from typing import List, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from openai import OpenAI
from settings import settings
from models import UserQuery, IngestPayload, ChatResponse, Hit
from rag import upsert_items, query, is_collection_empty
from tools import get_summary_by_title, contains_profanity
import os

app = FastAPI(title="Smart Librarian – RAG + Tool", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = OpenAI()

@app.get("/health")
def health():
    return {"status": "ok"}

def _build_tools_spec() -> List[Dict[str, Any]]:
    return [
        {
            "type": "function",
            "function": {
                "name": "get_summary_by_title",
                "description": "Returnează rezumatul complet (în limba română) pentru un titlu exact.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string", "description": "Titlul exact al cărții."}
                    },
                    "required": ["title"]
                }
            }
        }
    ]

def _ctx_blocks_from_hits(res: Dict[str, Any]) -> List[str]:
    blocks = []
    docs = res.get("documents", [[]])
    metas = res.get("metadatas", [[]])
    for doc, meta in zip(docs[0], metas[0]):
        title = meta.get("title", "Unknown")
        tags = meta.get("tags", "")
        blocks.append(f"Title: {title}\nTags: {tags}\nShort: {doc}")
    return blocks

def _hits_for_response(res: Dict[str, Any]) -> List[Hit]:
    out: List[Hit] = []
    dists = res.get("distances", [[]])
    docs = res.get("documents", [[]])
    metas = res.get("metadatas", [[]])
    for dist, meta, doc in zip(dists[0], metas[0], docs[0]):
        try:
            score = max(0.0, min(1.0, 1.0 - float(dist)))
        except Exception:
            score = 0.0

        tags_raw = meta.get("tags", "")
        tags = [t.strip() for t in tags_raw.split(",")] if isinstance(tags_raw, str) else []

        out.append(Hit(
            title=meta.get("title", "Unknown"),
            score=score,
            short_summary=doc,
            tags=tags
        ))
    return out

def _llm_recommend_with_tool(user_message: str, ctx_blocks: List[str]) -> Dict[str, Any]:
    system_prompt = (
        "Esti Smart Librarian, un asistent care recomanda carti.\n"
        "Ai primit context RAG (liste de titluri + rezumate scurte + tag-uri).\n"
        "Alege cea mai relevanta carte pentru cererea utilizatorului si explica de ce.\n"
        "Dupa ce alegi titlul, APELEAZA tool-ul 'get_summary_by_title' cu acel titlu pentru a obtine rezumatul detaliat.\n"
        "Raspunsul final trebuie sa fie un JSON cu cheile: recommendation_title, rationale, detailed_summary, used_tools.\n"
        "Limba raspunsului: romana."
    )

    context_str = "\n\n".join(ctx_blocks)

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Preferinte: {user_message}\n\nContext RAG:\n{context_str}\n\n"}
    ]

    tools = _build_tools_spec()

    first = client.chat.completions.create(
        model=settings.CHAT_MODEL,
        messages=messages,
        tools=tools,
        tool_choice="auto",
        temperature=0.3,
    )
    assistant_message = first.choices[0].message
    messages.append(assistant_message)

    used_tool_names: List[str] = []

    if hasattr(assistant_message, "tool_calls") and assistant_message.tool_calls:
        for tool_call in assistant_message.tool_calls:
            if tool_call.function.name == "get_summary_by_title":
                try:
                    args = json.loads(tool_call.function.arguments or "{}")
                except Exception:
                    args = {}
                title = args.get("title", "") if isinstance(args, dict) else ""
                detailed = get_summary_by_title(title)

                if tool_call.id:
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": "get_summary_by_title",
                        "content": detailed
                    })

                used_tool_names.append("get_summary_by_title")

    second = client.chat.completions.create(
        model=settings.CHAT_MODEL,
        messages=messages,
        response_format={"type": "json_object"},
        temperature=0.2,
    )

    final_content = second.choices[0].message.content or "{}"

    try:
        final_json = json.loads(final_content)
    except Exception:
        final_json = {
            "recommendation_title": "",
            "rationale": final_content,
            "detailed_summary": "",
            "used_tools": used_tool_names
        }

    rec_title = final_json.get("recommendation_title") or ""
    if not final_json.get("detailed_summary") and rec_title:
        try:
            ds = get_summary_by_title(rec_title)
            final_json["detailed_summary"] = ds
            if "get_summary_by_title" not in used_tool_names:
                used_tool_names.append("get_summary_by_title")
        except Exception:
            pass

    existing = final_json.get("used_tools") or []
    merged = list({*existing, *used_tool_names}) if isinstance(existing, list) else used_tool_names
    final_json["used_tools"] = merged

    return final_json

@app.on_event("startup")
def _startup_seed():
    if is_collection_empty():
        data_path = os.path.join(os.path.dirname(__file__), "data", "book_summaries.json")
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                items = json.load(f)
            upsert_items(items)
            print(f"[Seed] Inserted {len(items)} items into Chroma collection.")
        except Exception as e:
            print(f"[Seed] Failed: {e}")

@app.post("/ingest")
def ingest(payload: IngestPayload):
    try:
        count = upsert_items([it.model_dump() for it in payload.items])
        return {"upserted": count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat", response_model=ChatResponse)
def chat(q: UserQuery):
    if settings.ENABLE_PROFANITY_FILTER and contains_profanity(q.message):
        return ChatResponse(
            recommendation_title="",
            rationale="",
            detailed_summary="Mesajul conține limbaj nepotrivit. Reformulează, te rog.",
            used_tools=[],
            hits=[]
        )

    try:
        res = query(q.message, k=settings.TOP_K)
        ctx_blocks = _ctx_blocks_from_hits(res)
        hits = _hits_for_response(res)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare la interogarea Chroma: {e}")

    try:
        final_json = _llm_recommend_with_tool(q.message, ctx_blocks)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Eroare LLM: {e}")

    final_json["hits"] = [h.model_dump() for h in hits]

    try:
        return ChatResponse(**final_json)
    except Exception:
        return ChatResponse(
            recommendation_title=str(final_json.get("recommendation_title", "")),
            rationale=str(final_json.get("rationale", "")),
            detailed_summary=str(final_json.get("detailed_summary", "")),
            used_tools=list(final_json.get("used_tools", [])),
            hits=hits
        )
