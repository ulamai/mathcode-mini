# Prime Intellect

The public compatibility task is designed to be published as
`ulamai/mathcode-mini` on the Prime Environment Hub. After publication, a
hosted smoke test should use five examples and one rollout first:

```bash
prime eval run ulamai/mathcode-mini --hosted --follow \
  -n 5 -r 1 --allow-sandbox-access
```

The public repository contains only the expired task and public grader. The
commercial MathCode adapter uses a separate host-only scorer and must not be
copied into this repository.
