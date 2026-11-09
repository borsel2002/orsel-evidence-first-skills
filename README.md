# Orsel evidence-first skills

Three small, auditable Markdown skills for teams who want useful content and follow-up without invented evidence or unsolicited automation. These are instructions, not an autonomous service or a promise of business results.

- **source-grounded-brief**: cite an actual source; answer first, then Why/How/What.
- **permission-first-followup**: check channel-specific permission, opt-outs and replies; draft only.
- **measurement-honesty**: disclose source/window/sample, deduplicate, separate test traffic from production.

## Run from this checkout

Requires Python 3.11 or newer. No pip install, cloud account, API key, model, subscription, or network access is required.

```sh
python3 skill_pack.py verify
python3 skill_pack.py list
python3 skill_pack.py show source-grounded-brief
python3 skill_pack.py example source-grounded-brief
python3 skill_pack.py example permission-first-followup
python3 skill_pack.py example measurement-honesty
python3 -m unittest discover -s tests -v
```

All examples are explicitly synthetic public teaching inputs. They are not client records, measured production results, consent evidence for real recipients, or Search Console data. The citation example checks an exact passage in the supplied skill file; the measurement example actually deduplicates its toy events.

### macOS temporary-directory caveat

The initial independent test run failed under the default macOS temporary directory because `/var` resolves through a symlink. The same 17 tests pass with a real-path `TMPDIR`. The symlink guard is intentional and has not been weakened. Before testing on macOS, normalize the existing temporary directory for that process:

```sh
TMPDIR="$(python3 -c 'import pathlib,tempfile; print(pathlib.Path(tempfile.gettempdir()).resolve())')" python3 -m unittest discover -s tests -v
```

Use a real, non-symlink workspace for installation too. This is a disclosed test-environment restriction, not a claim that default-path tests passed.

## Install only where you choose

```sh
python3 skill_pack.py install --workspace ./demo-workspace
```

This copies the original three files to `demo-workspace/.agents/skills/<name>/SKILL.md`, verifies the bytes and executes none of the instructions. Use `--skill measurement-honesty` to install just one. Existing files and symlink destinations are rejected rather than overwritten. Review each skill before loading it in your agent. Agent-specific skill discovery varies: you can also open a file and deliberately provide its instructions yourself.

Optional references to `content_prep` and `copy_lint` inside the brief skill do not require those private company utilities. They are not included; the skill and examples work without them.

## Boundaries

There is no sender, tracker, sign-up collector, credential loader, model dispatcher, or live integration. Marketing permission is distinct from analytics consent. Real publication and sending require a human's current approval and the team's existing safeguards. An instruction to verify a source is not itself source verification.

The installer is an operator-invoked local CLI, not a service accepting untrusted remote paths. Use a workspace you control, not a directory concurrently modified by untrusted users. Local hashes detect drift against this release manifest, not a forged manifest; compare the release's externally reviewed hash before trusting a download.

## Opt-in distribution

`docs/opt-in-distribution.md` supplies a public invitation, a requested-link reply and a withdrawal response. They are drafts, not sent messages. `web/index.html` is a static preview with no scripts, form endpoint, cookies, pixels, remote fonts or data collection. No existing company website needs to change.

## License and provenance

The three skill texts are original project-authored templates, copied byte-for-byte into this pack. No owner memory, client exports, private company source code, external skill-library text or third-party implementation is bundled. See `NOTICE.md` and `LICENSE`. The remaining CLI, documentation and tests are original supporting material. This original material is released under the MIT license; the owner authorized this public repository and license, subject to exact-byte release review.
