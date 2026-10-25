# curl 使用与 GitHub 发布

仓库：[minglezhou/FNOS-OpenclawMod](https://github.com/minglezhou/FNOS-OpenclawMod)。按所有者选择沿用已创建的仓库名称。

## 发布后安全下载

使用实际 GitHub owner 和经过审阅的完整 commit SHA。公开只读单文件可直接下载后运行；生产变更脚本必须显式提供路径、版本和维护参数。不提供 `curl ... | sudo bash` 自动升级。

```bash
# Replace both placeholders after publishing; use an immutable reviewed commit.
REPO_OWNER='minglezhou'
REF='FULL_40_HEX_COMMIT_SHA'
tmp=$(mktemp -d)
curl --fail --show-error --silent --location --proto '=https' --proto-redir '=https'   "https://raw.githubusercontent.com/$REPO_OWNER/FNOS-OpenclawMod/$REF/scripts/inspect.py"   -o "$tmp/inspect.py"
python3 -B "$tmp/inspect.py"
```

需要 root 读取 exe 时，审阅下载内容后对同一文件运行 `sudo python3 -B`。这仍只做观察，不控制服务。完整仓库用户可运行 `sha256sum -c SHA256SUMS.txt` 检查包内容；同源清单不是独立数字签名，应结合可信 commit/release 来源。

## 获取完整仓库与后续维护

```bash
git clone https://github.com/minglezhou/FNOS-OpenclawMod.git
cd FNOS-OpenclawMod
# For reproducible maintenance, select the reviewed commit shown above:
git checkout "$REF"
sha256sum -c SHA256SUMS.txt
```

修改脚本后运行离线检查，更新 SHA256SUMS 和 CHANGELOG，检查差异中没有个人配置或秘密，并标注模拟验证和实际 NAS 验证的区别。不要把访问令牌放进下载 URL。
