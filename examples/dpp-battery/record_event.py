import json,hashlib,os,subprocess,base64
from datetime import datetime,timezone
def sha256_file(p):
    with open(p,"rb") as f: return hashlib.sha256(f.read()).hexdigest()
def canonical(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def now(): return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00","Z")
with open("manifest.json") as f: m=json.load(f)
targets={t["id"]:sha256_file(t["path"]) for t in m["targets"]}
payload_hash=hashlib.sha256(canonical({}).encode()).hexdigest()
prev="0"*64
if os.path.getsize("journal.jsonl")>0:
    with open("journal.jsonl") as f:
        for l in f: prev=json.loads(l)["entry_hash"]
entry={"seq":1,"timestamp":now(),"event":"created","targets":targets,
       "event_payload_sha256":payload_hash,"prev_entry_hash":prev}
entry_hash=hashlib.sha256((prev+canonical(entry)).encode()).hexdigest()
entry["entry_hash"]=entry_hash
with open("journal.jsonl","a") as f: f.write(canonical(entry)+"\n")
m["integrity"]["targets_sha256"]=targets
m["integrity"]["journal_sha256"]=sha256_file("journal.jsonl")
m["integrity"]["last_entry_hash"]=entry_hash
subprocess.run(["openssl","pkeyutl","-sign","-inkey",m["signature"]["private_key_path"],
"-rawin","-in","journal.jsonl","-out","__sig"],check=True)
with open("__sig","rb") as f: sig=f.read()
os.remove("__sig")
m["integrity"]["signature_base64"]=base64.b64encode(sig).decode()
badge_fingerprint=hashlib.sha256(entry_hash.encode()).hexdigest()
m["integrity"]["badge_fingerprint"]=badge_fingerprint
with open("manifest.json","w") as f: json.dump(m,f,indent=2)
print("EVENT_RECORDED")
