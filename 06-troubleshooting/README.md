# Chapter 06 — Troubleshooting

Diagnose Pod, scheduling, Service, DNS, node, and application problems.

This chapter documents our JAVAD_CKA homelab session on 11 November 2026. Commands run on the Mac unless a section explicitly says Ubuntu node. Addresses are session snapshots, not permanent configuration.

## Install these notes

Extract the archive, then copy the Markdown files from its `06-troubleshooting/` directory into your repository's existing `06-troubleshooting/` directory. The archive contains documentation only: it does not replace your four existing files under `manifests/`.

## Lessons

1. [Start here and diagnostic workflow](00-start-here.md)
2. [ImagePullBackOff](01-image-pull-failures.md)
3. [CrashLoopBackOff](02-container-restarts.md)
4. [Pending and scheduling](03-scheduling.md)
5. [Service selectors and endpoints](04-services.md)
6. [IP addresses and DNS](05-networking-explained.md)
7. [Node health](06-node-health.md)
8. [Jobs demo verification](07-jobs-demo.md)
9. [Review, cleanup, and Git](08-review-and-git.md)

## Existing manifests

| File | Exercise | Repaired setting |
|---|---|---|
| `manifests/broken-image.yaml` | Invalid image tag | `nginx:stable` |
| `manifests/broken-command.yaml` | Immediate container exit | Shell command that prints a message and sleeps |
| `manifests/broken-scheduling.yaml` | Unmatched node selector | `kubernetes.io/hostname: worker1` |
| `manifests/broken-service.yaml` | Selector mismatch | `run: broken-image` |

The files themselves were not inspected when preparing these notes. Check that their saved configuration matches your intended repaired state; live edits do not update local YAML automatically.

## Scope completed

We repaired three Pod problems and a Service selector problem, explored DNS, inspected healthy node services, and verified the jobs application. We did not simulate a broken kubelet, failed runtime, or failed database in this session.
