# Publication gates after Astra R02

The current technical tree replaces private conversation/message URLs with stable `HIST-C001`–`HIST-C020` IDs and sanitized summaries. The corresponding original links and instruction-source identity are stored only in gitignored private evidence. The public index is not a public primary-source transcript; its U/A provenance and omitted-attachment limitations remain explicit.

Earlier local commits contain private references. **The native Git history is not approved for publication.** This repair does not rewrite history, create a remote, push, or publish. Before any publication, the owner must choose an authorized approach: a reviewed source export/new public history containing only approved files, or an explicitly approved history-cleaning procedure. No choice is silently applied by these tools.

`python3 -I -B scripts/check-public-tree.py` inspects current tracked/new public candidates for the selected private-reference patterns. Add `--history` to inspect the local history separately; that gate is expected to fail while old references remain. A clean current-tree pattern result is not a comprehensive secret scan, proof of third-party rights, or approval to publish history.

Other existing gates remain: repository license is unselected, SDK/third-party inclusion rights need review, supporting documents need an approved public destination, and article-relative links must be verified at that destination. The independent clean-install and numerical acceptance gaps are separate from privacy/publication readiness.
