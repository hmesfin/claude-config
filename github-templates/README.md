# GitHub templates

Canonical source. Nothing here is authored directly in `hmesfin/.github`.

## What goes where

- `PULL_REQUEST_TEMPLATE.md`, `ISSUE_TEMPLATE/` - published to the public
  `hmesfin/.github` repo by `../publish-github-templates.sh`. GitHub applies
  them as defaults to every `hmesfin/*` repo that has no equivalent file of
  its own.
- `pre-commit-snippet.yaml`, `README.md` - local only, never published.

## The override rule

Per-repo overrides are all-or-nothing per folder:

> If a repository has any files in its own `.github/ISSUE_TEMPLATE` folder,
> such as issue templates or a `config.yml` file, none of the contents of the
> default `.github/ISSUE_TEMPLATE` folder will be used.

So a repo that adds one custom issue form loses ALL inherited forms, including
the bug form. If a repo needs one custom form, copy the defaults in alongside
it.

`PULL_REQUEST_TEMPLATE.md` is a single file and overrides cleanly on its own.

## Publishing

    ./publish-github-templates.sh

The `hmesfin/.github` repo is public. Nothing here may contain client names,
infrastructure detail, or internal process.
