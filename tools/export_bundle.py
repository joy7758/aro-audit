import sys
import zipfile
from pathlib import Path

def main():
    if len(sys.argv) != 4:
        print("Usage: python export_bundle.py <journal> <public.pem> <output.zip>")
        sys.exit(2)

    journal = Path(sys.argv[1])
    pubkey = Path(sys.argv[2])
    out = Path(sys.argv[3])

    if not journal.exists():
        print("journal not found")
        sys.exit(1)
    if not pubkey.exists():
        print("public.pem not found")
        sys.exit(1)

    with zipfile.ZipFile(out, "w") as z:
        z.write(journal, "journal.jsonl")
        # Keep both names for cross-version verifier compatibility.
        z.write(pubkey, "public.pem")
        z.write(pubkey, "org_pubkey_ed25519.pem")

    print("Bundle created:", out)

if __name__ == "__main__":
    main()
