import json,hashlib,subprocess,base64,os,sys
def sha256_file(p):
    with open(p,"rb") as f: return hashlib.sha256(f.read()).hexdigest()
def canonical(o): return json.dumps(o,sort_keys=True,separators=(",",":"),ensure_ascii=False)
with open("manifest.json") as f: m=json.load(f)
targets={t["id"]:sha256_file(t["path"]) for t in m["targets"]}
if targets!=m["integrity"]["targets_sha256"]:
    print("VERIFY_FAIL target mismatch"); sys.exit(1)
if sha256_file("journal.jsonl")!=m["integrity"]["journal_sha256"]:
    print("VERIFY_FAIL journal mismatch"); sys.exit(1)
prev="0"*64
with open("journal.jsonl") as f:
    for l in f:
        e=json.loads(l)
        tmp=dict(e); h=tmp.pop("entry_hash")
        if hashlib.sha256((prev+canonical(tmp)).encode()).hexdigest()!=h:
            print("VERIFY_FAIL chain"); sys.exit(1)
        prev=h
sig=base64.b64decode(m["integrity"]["signature_base64"])
open("__sig","wb").write(sig)
res=subprocess.run(["openssl","pkeyutl","-verify","-pubin",
"-inkey",m["signature"]["public_key_path"],
"-rawin","-in","journal.jsonl","-sigfile","__sig"])
os.remove("__sig")
if res.returncode!=0:
    print("VERIFY_FAIL signature"); sys.exit(1)
report={
"status":"OK",
"profile_handle":m["profile_handle"],
"targets_sha256":targets,
"journal_sha256":m["integrity"]["journal_sha256"],
"last_entry_hash":m["integrity"]["last_entry_hash"],
"badge_fingerprint":m["integrity"]["badge_fingerprint"]
}
with open("verification_report.json","w") as f: json.dump(report,f,indent=2)
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="350" height="60"><rect width="350" height="60" fill="green"/><text x="175" y="35" font-size="18" fill="white" text-anchor="middle">ARO Integrity OK</text></svg>'
with open("integrity_badge.svg","w") as f: f.write(svg)
schema={
"type":"object",
"properties":{
"targets_sha256":{"type":"object"},
"journal_sha256":{"type":"string"},
"last_entry_hash":{"type":"string"},
"badge_fingerprint":{"type":"string"}
}
}
with open("verification_schema.json","w") as f: json.dump(schema,f,indent=2)
print("VERIFY_OK + REPORT + BADGE + SCHEMA GENERATED")
