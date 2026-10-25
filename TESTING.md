# Validation / 验证说明

Run date: 2026-10-25. Result: **18 tests passed, 0 failures, 0 errors** under Python 3.11 in the authoring environment. Both shell scripts passed `bash -n`; inspector and installer help entrypoints were exercised.

```bash
python3 -B -m unittest discover -s tests -v
bash -n scripts/upgrade-core.sh scripts/stage-node.sh
```

## Coverage / 覆盖范围

- Exact version validation, HTTPS registry origin restrictions, SHA-512 SRI match/mismatch and refusal to silently fall back to weaker SRI.
- Non-overlapping backup paths, no destination overwrite, resolved symlink containment, and inventory output excluding arbitrary package fields.
- Local health JSON independent of whitespace; failure output excludes response/exception text.
- Installer plan never executes Bun; explicit confirmation and verified checkpoint coverage are required. Identity is mocked only inside tests; production checks remain present.
- Real GNU tar + rsync synthetic-directory roundtrip: file bytes, 0600 mode, a hardlink and a symlink preserved. Extraction failure retains the archive and verification directory without a success receipt.

## Limits / 未覆盖

No NAS production operations, real package installation, runtime activation, real provider requests or service restarts were performed with these new scripts. Root/quiescence gates were mocked in the isolated capture integration test; it proves neither host process visibility nor absence of external writers. No full ACL/xattr/native-filesystem fidelity matrix was exercised. Node staging was syntax-checked, not a live download/activation test. Registry network download was not exercised by the offline suite.

历史 NAS 成功回执只支持文档中的案例结论；不能挪作这些新脚本的生产验收。实际部署先查当前包布局、路径权限、工具版本和维护条件。此次测试只验证当前未闭合的实现边界，不要求使用者为普通文档改动重复整套维护测试。
