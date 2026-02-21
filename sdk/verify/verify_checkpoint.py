import sys

from sdk.verify.verify_chain import verify_chain


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: verify_checkpoint <journal.jsonl> <org_pubkey.pem>")
        return 1
    return verify_chain(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    raise SystemExit(main())
