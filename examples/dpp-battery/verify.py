import json,hashlib,subprocess,base64,os,sys,zipfile
def sha256_file(p):
    with open(p,"rb") as f: return hashlib.sha256(f.read()).hexdigest()
def canonical(o): return json.dumps(o,sort_keys=True,separators=(",",":"))
m=json.load(open("manifest.json"))
targets={t["id"]:sha256_file(t["path"]) for t in m["targets"]}
if targets!=m["integrity"]["targets_sha256"]:
    sys.exit("FAIL targets mismatch")
if sha256_file("journal.jsonl")!=m["integrity"]["journal_sha256"]:
    sys.exit("FAIL journal mismatch")
prev="0"*64
for l in open("journal.jsonl"):
    e=json.loads(l); tmp=dict(e); h=tmp.pop("hash")
    if hashlib.sha256((prev+canonical(tmp)).encode()).hexdigest()!=h:
        sys.exit("FAIL chain")
    prev=h
sig=base64.b64decode(m["integrity"]["signature_base64"])
open("__sig","wb").write(sig)
r=subprocess.run(["openssl","pkeyutl","-verify","-pubin",
"-inkey",m["signature"]["public_key"],
"-rawin","-in","journal.jsonl","-sigfile","__sig"])
os.remove("__sig")
if r.returncode!=0: sys.exit("FAIL signature")
report={
"status":"OK",
"profile":m["profile_handle"],
"targets_sha256":targets,
"last_hash":m["integrity"]["last_entry_hash"],
"badge":m["integrity"]["badge_fingerprint"]
}
json.dump(report,open("verification_report.json","w"),indent=2)
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="320" height="60"><rect width="320" height="60" fill="green"/><text x="160" y="35" font-size="18" fill="white" text-anchor="middle">ARO Integrity OK</text></svg>'
open("integrity_badge.svg","w").write(svg)
schema={"type":"object","properties":{"targets_sha256":{"type":"object"},"last_hash":{"type":"string"}}}
json.dump(schema,open("verification_schema.json","w"),indent=2)
profile={
"Identifier":"21.T11966/aro-audit-generated",
"name":"ARO_GENERATED_PROFILE",
"description":"Auto-generated FDO profile attachment demo"
}
json.dump(profile,open("generated_fdo_profile.json","w"),indent=2)
with zipfile.ZipFile("zenodo_bundle.zip","w") as z:
    for f in ["dpp.json","battery_certificate.pdf","sbom.json",
              "journal.jsonl","manifest.json",
              "verification_report.json","integrity_badge.svg"]:
        z.write(f)
print("VERIFY_OK + ALL ARTIFACTS GENERATED")
