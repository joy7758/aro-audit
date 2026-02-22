import json,hashlib,os,subprocess,base64
def sha256_file(p):
    with open(p,"rb") as f: return hashlib.sha256(f.read()).hexdigest()
def canonical(o): return json.dumps(o,sort_keys=True,separators=(",",":"))
m=json.load(open("manifest.json"))
targets={t["id"]:sha256_file(t["path"]) for t in m["targets"]}
prev="0"*64
entry={"seq":1,"event":"created","targets":targets,"prev":prev}
h=hashlib.sha256((prev+canonical(entry)).encode()).hexdigest()
entry["hash"]=h
open("journal.jsonl","a").write(canonical(entry)+"\n")
m["integrity"]["targets_sha256"]=targets
m["integrity"]["journal_sha256"]=sha256_file("journal.jsonl")
m["integrity"]["last_entry_hash"]=h
subprocess.run(["openssl","pkeyutl","-sign","-inkey",m["signature"]["private_key"],
"-rawin","-in","journal.jsonl","-out","__sig"],check=True)
sig=open("__sig","rb").read(); os.remove("__sig")
m["integrity"]["signature_base64"]=base64.b64encode(sig).decode()
m["integrity"]["badge_fingerprint"]=hashlib.sha256(h.encode()).hexdigest()
json.dump(m,open("manifest.json","w"),indent=2)
print("EVENT_RECORDED")
