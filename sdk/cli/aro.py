import sys
import subprocess


def main():
    if len(sys.argv) < 2:
        print("Usage: aro <verify-chain|verify-checkpoint>")
        return 1

    cmd = sys.argv[1]

    if cmd == "verify-chain":
        if len(sys.argv) != 4:
            print("Usage: aro verify-chain <journal> <pubkey>")
            return 1
        result = subprocess.run(
            [sys.executable, "-m", "sdk.verify.verify_chain", sys.argv[2], sys.argv[3]],
            check=False,
        )
        return result.returncode

    if cmd == "verify-checkpoint":
        if len(sys.argv) != 4:
            print("Usage: aro verify-checkpoint <journal> <pubkey>")
            return 1

        result = subprocess.run(
            [sys.executable, "-m", "sdk.verify.verify_checkpoint", sys.argv[2], sys.argv[3]],
            check=False
        )
        return result.returncode

    print("Usage: aro <verify-chain|verify-checkpoint>")
    return 1


def app():
    return main()


if __name__ == "__main__":
    raise SystemExit(main())
