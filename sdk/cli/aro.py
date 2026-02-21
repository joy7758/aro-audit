import sys
import subprocess


def main():
    if len(sys.argv) < 2:
        print("Usage: aro <gen-demo|verify|export|verify-checkpoint>")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "verify-checkpoint":
        if len(sys.argv) != 4:
            print("Usage: aro verify-checkpoint <journal> <pubkey>")
            sys.exit(1)

        subprocess.run(
            ["python", "-m", "sdk.verify.verify_checkpoint", sys.argv[2], sys.argv[3]],
            check=False
        )
        return

    print("Other commands unchanged (gen-demo/verify/export)")
    sys.exit(0)


if __name__ == "__main__":
    main()
