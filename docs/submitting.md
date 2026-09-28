# Submitting a suite

How a suite gets listed in the Claude plugin directory and the Grok plugin catalog. Each suite is submitted on its own, as `skill-suites-<suite>` from the folder `skills/<suite>`. Do this after the suite passes every check in [adding a suite](adding-a-suite.md) and its commit is on `main` in the public repository.

Anyone can already install every suite from this repository's own marketplace files, without either listing:

```sh
claude plugin marketplace add shinytoyrobots/skill-suites
grok plugin marketplace add shinytoyrobots/skill-suites
```

## Claude plugin directory, once per suite

1. Go to [claude.ai/directory/manage](https://claude.ai/directory/manage) and choose **Plugin bundle**.
2. Repository `shinytoyrobots/skill-suites`, plugin path `skills/<suite>`, tracked branch `main`.
3. Validate. Fix every blocking finding in this repo, push to `main`, and validate again.
4. Answer the data-handling questions with the answers below, then submit.

The repository must be public before the listing publishes. Publishing needs a paid Claude account and the GitHub connection on the account that owns the repository. Later changes to a submitted suite publish from pushes to `main`; they are not a new submission. Bump `version` in the suite's `suite.yaml` for each behavior change.

## Data-handling answers

The same for every suite here, unless a suite's README says otherwise:

- **What it reads and writes.** Only what the operator asks it to, in the project-relative and home-relative directories its README names (for `ops-`: `./.ops/` and `~/.ops-skills/`, or `OPS_STATE`).
- **Where data goes.** Nowhere. The skills make no network calls and send nothing to another service.
- **Retention.** Files stay on the operator's machine until the operator deletes them.
- **Audience.** Not directed at people under 18.

## Grok plugin catalog

The catalog is the [xai-org/plugin-marketplace](https://github.com/xai-org/plugin-marketplace) repository. A suite is listed by a pull request that adds one remote entry to its `.grok-plugin/marketplace.json`.

1. Print the entries, pinned to the current commit:

   ```sh
   scripts/render-plugins.sh --upstream
   ```

   Each entry's `source.url` is this repository, `source.sha` is the full commit at `HEAD`, and `source.path` is `skills/<suite>`. The script warns if `HEAD` is not on `origin/main` or `skills/` has uncommitted changes; pin only a pushed commit. The pin is printed, never written into this repository, because it would go stale on the next commit.
2. In a fork of the catalog, add the new suite's entry to the `plugins` array.
3. Run its tools, regenerate the index, and commit both files:

   ```sh
   python3 scripts/generate-plugin-index.py
   python3 scripts/validate-catalog.py
   python3 scripts/generate-plugin-index.py --check
   ```

4. Open the PR. Include the ownership note below.

A later change to a listed suite is a PR that bumps `sha` on its existing entry, with the index regenerated. Never add a second entry for the same suite.

**Ownership note for the PR.** The catalog questions a branded plugin whose source is a personal account. These plugins are named for this repository (`skill-suites-<suite>`), not for any product or company, and the repository is the author's own. Say so in the PR description. There is no separate organization.
