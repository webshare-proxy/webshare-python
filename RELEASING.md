# Releasing `webshare-sdk`

## Versioning policy

We follow [Semantic Versioning](https://semver.org). While the SDK is on `0.x`
the public API is not yet frozen: **minor** bumps (`0.1 → 0.2`) may contain
breaking changes, **patch** bumps (`0.1.0 → 0.1.1`) never do. Once the API is
settled we cut `1.0.0`, after which:

- **major** — a breaking change to the public API (removed/renamed symbol,
  changed signature, changed runtime behaviour a caller could rely on).
- **minor** — backwards-compatible new functionality.
- **patch** — backwards-compatible bug fixes.

Anything importable from `webshare` (the top-level package) is public API.

## How to cut a release

Publishing is fully automated — a pushed tag is the only trigger. Never run
`twine upload` from a laptop.

1. Update `CHANGELOG.md` (move items from _Unreleased_ into a new version
   heading).
2. Bump `version` in `pyproject.toml` (`[project].version`).
3. Commit, tag, and push:
   ```bash
   git commit -am "Release v0.1.1"
   git tag v0.1.1
   git push origin main --follow-tags
   ```
4. The **Release** workflow builds the sdist + wheel and publishes to PyPI via
   Trusted Publishing. Watch the Actions tab; the listing appears at
   <https://pypi.org/project/webshare-sdk/>.

The workflow fails fast if the tag and `pyproject.toml` version disagree.

## Credentials

There are **no stored credentials**. Publishing uses
[PyPI Trusted Publishing](https://docs.pypi.org/trusted-publishers/) (OIDC): PyPI
is configured to trust this repo's `release.yml` workflow running in the
`release` environment, and CI exchanges a short-lived GitHub OIDC token for an
upload token at publish time.
