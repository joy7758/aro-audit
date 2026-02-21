import sys
import zipfile
import tempfile
import shutil
from pathlib import Path
import subprocess

def fail(msg):
    print("VERIFY_FAIL:", msg)
    sys.exit(1)

def main():
    if len(sys.argv) != 2:
        print("Usage: python verify_bundle.py <audit_bundle.zip>")
        sys.exit(2)

    bundle = Path(sys.argv[1])
    if not bundle.exists():
        fail("Bundle not found")

    with tempfile.TemporaryDirectory() as tmp:
        with zipfile.ZipFile(bundle, 'r') as z:
            z.extractall(tmp)

        tmp = Path(tmp)

        journal = tmp / "journal.jsonl"
        pubkey = tmp / "public.pem"

        if not journal.exists():
            fail("journal.jsonl missing")
        if not pubkey.exists():
            fail("public.pem missing")

        # 调用现有 verify_chain
        result = subprocess.run(
            ["python", "-m", "sdk.verify.verify_chain", str(journal), str(pubkey)],
            capture_output=True,
            text=True
        )

        print(result.stdout.strip())
        if result.returncode != 0:
            fail("Chain verification failed")

        print("VERIFY_OK: bundle valid")

if __name__ == "__main__":
    main()
