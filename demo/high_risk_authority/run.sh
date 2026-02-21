#!/usr/bin/env bash
set -e

echo "=============================="
echo " AAR-MCP-2.0 High Risk Demo"
echo "=============================="
echo

echo "1️⃣ Generating high-risk action..."
python3 run_demo.py

echo
echo "2️⃣ Verifying integrity..."
python3 -m sdk.verify.verify_chain journal.jsonl public.pem

echo
echo "3️⃣ Simulating tampering..."
cp journal.jsonl journal.attack.jsonl
sed -i '' 's/100000/10/' journal.attack.jsonl

echo
echo "4️⃣ Verifying tampered journal..."
python3 -m sdk.verify.verify_chain journal.attack.jsonl public.pem || true

echo
echo "=============================="
echo " Demo complete"
echo "=============================="
