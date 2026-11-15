import argparse,json,os,re,sys,urllib.request,urllib.error
from pathlib import Path
from datetime import datetime,timezone

RULES="""Write a 25-40 second REPWALA YouTube Short in natural Hinglish (Roman script) for Indian fitness beginners. Energetic, practical, respectful, evidence-aware. No body shaming, diagnosis, treatment advice, steroids, extreme diets, dangerous weight-loss methods or guaranteed results. Never invent studies, citations, prices or nutrition numbers. Flag every factual claim needing verification. Educational content, not medical advice. Return ONLY JSON keys: title,hook,narration,scene_plan,on_screen_text,caption,hashtags,fact_check_flags,safety_notes. scene_plan: 4-6 objects with visual and duration_seconds. Arrays for on_screen_text,hashtags,fact_check_flags. End with REPWALA follow prompt. Tagline TRAIN SMART. LOOK STRONG."""
def main():
 p=argparse.ArgumentParser();p.add_argument("--topic",required=True);p.add_argument("--angle",default="");a=p.parse_args()
 key=os.getenv("GEMINI_API_KEY")
 if not key: print("Missing GEMINI_API_KEY secret.",file=sys.stderr);return 1
 model=os.getenv("GEMINI_MODEL","gemini-3.5-flash-lite")
 body={"contents":[{"parts":[{"text":RULES+"\nTopic: "+a.topic+"\nAngle: "+a.angle}]}],"generationConfig":{"temperature":0.55,"responseMimeType":"application/json"}}
 req=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/"+model+":generateContent?key="+key,data=json.dumps(body).encode(),headers={"Content-Type":"application/json"})
 try:
  with urllib.request.urlopen(req,timeout=60) as r: data=json.loads(r.read())
  draft=json.loads(data["candidates"][0]["content"]["parts"][0]["text"])
 except Exception as e: print("Generation failed:",str(e)[:500],file=sys.stderr);return 1
 required={"title","hook","narration","scene_plan","on_screen_text","caption","hashtags","fact_check_flags","safety_notes"}
 if required-draft.keys(): print("Missing output fields:",sorted(required-draft.keys()),file=sys.stderr);return 1
 draft.update({"brand":"REPWALA","topic":a.topic,"generated_at_utc":datetime.now(timezone.utc).isoformat(),"publishing_status":"DRAFT_ONLY"})
 out=Path("output");out.mkdir(exist_ok=True);slug=re.sub(r"[^a-zA-Z0-9_-]+","-",a.topic.lower()).strip("-")[:50] or "draft"
 path=out/(slug+".json");path.write_text(json.dumps(draft,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print("Draft saved:",path,"| Fact-check flags:",len(draft["fact_check_flags"]),"| No upload performed.")
if __name__=="__main__":raise SystemExit(main())
