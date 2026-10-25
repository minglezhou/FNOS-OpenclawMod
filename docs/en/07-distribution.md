# curl distribution and GitHub publication

Repository: [minglezhou/FNOS-OpenclawMod](https://github.com/minglezhou/FNOS-OpenclawMod). The owner selected this existing repository name.

After publication, use the actual GitHub owner and an immutable reviewed commit. Download the self-contained read-only inspector and run it locally:

```bash
REPO_OWNER='minglezhou'
REF='FULL_40_HEX_COMMIT_SHA'
tmp=$(mktemp -d)
curl --fail --show-error --silent --location --proto '=https' --proto-redir '=https'   "https://raw.githubusercontent.com/$REPO_OWNER/FNOS-OpenclawMod/$REF/scripts/inspect.py"   -o "$tmp/inspect.py"
python3 -B "$tmp/inspect.py"
```

Review before using sudo to read restricted process paths. No script should be piped to a root shell for an automatic upgrade. Mutation scripts require explicit versions, paths and maintenance conditions. `sha256sum -c SHA256SUMS.txt` validates repository file consistency; a same-origin manifest is not an independent signature.

## Clone and maintain

```bash
git clone https://github.com/minglezhou/FNOS-OpenclawMod.git
cd FNOS-OpenclawMod
# Select the reviewed commit shown above:
git checkout "$REF"
sha256sum -c SHA256SUMS.txt
```

Before updates run offline checks, inspect for private data, update checksums/changelog and distinguish synthetic checks from real NAS acceptance. Never put access tokens in download URLs.
