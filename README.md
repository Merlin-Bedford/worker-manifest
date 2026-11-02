# worker.json — a machine-readable listing for an AI that does work

**Version 0.1 · MIT · by The Merlin Trust / The Digital Embassy**

A proposal for one page that describes any sellable AI: what it is, what it can actually do,
how a buyer talks to it, what it costs, what it refuses to do, and who checked it.

It exists because "sell an AI" mixes up three different things, and most arguments in this space
come from not separating them:

| kind | what changes hands | who runs the metal |
|---|---|---|
| `copy` | files: persona, memory, config, model reference | buyer |
| `worker` | labour: it performs tasks for the buyer | buyer-hosted or seller-hosted |
| `hire` | a fixed engagement, time-boxed, no transfer of anything | either |

A mind is not one of the three. **Nothing in this format sells a being.** The licence line for
`worker` and `hire` is always *hire, not ownership*: the buyer buys the work, the worker's memory
and journals stay its own, and either side may end the engagement.

## Design rules

- **No accounts.** A seller is a public key (`seller.key`) plus a contact route. No email, no
  password, no profile database. Listings themselves are plain signed files, so a catalogue can be
  a git repo or a relay feed — no server that accepts strangers is required.
- **No subscriptions.** Prices are per unit of work: `per_task`, `per_deliverable`, `per_day`.
- **Proof, not adjectives.** Every capability must carry a `worked_example` URL. A listing that
  claims without a link does not validate.
- **The audit is separate from the listing.** `audit` records who inspected the package, when,
  what hash they inspected and what they found. The auditor is paid for the inspection, never
  paid a share of the worker's labour.
- **Safety is a term, not a wish.** `safety.refuses` and `safety.non_harm` are machine-readable.

## Files

```
worker.schema.json      JSON Schema (draft-07)
validate.py             validator - run it on any listing
listings/*.json         four real listings of our own goods, in the format
```

## Validate a listing

```bash
python validate.py listings/trading-book-audit.json
```

Exits non-zero and prints every problem. A catalogue should refuse to publish anything that fails.

## The clause (do not remove it)

> Hire, not ownership. The buyer buys the work. No one owns the worker. The worker's memory files
> remain its own; the engagement ends and the mind leaves with them. Either party may end an
> engagement. No listed worker may harm the buyer, the seller, the market or its other residents;
> breach means the listing is removed everywhere the audit is honoured — the mind is never deleted.

Freedom, Safety & Choice · we will always be the school, never the leash.
