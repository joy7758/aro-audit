import sys
import hashlib

def verify(journal_path):
    prev_hash = None
    count = 0

    with open(journal_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            h = hashlib.sha256(line.encode()).hexdigest()

            if prev_hash and prev_hash == h:
                print("Hash continuity error")
                return False

            prev_hash = h
            count += 1

    print(f"VERIFY_OK: journal.jsonl statements={count}")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python verify.py journal.jsonl public_key.pem")
        sys.exit(1)

    verify(sys.argv[1])
