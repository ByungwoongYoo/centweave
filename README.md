# CentWeave

A Fe library for allocating indivisible units across a fixed group without restarting the rounding decision at every receipt. A `Series` fixes the recipient order and weights and advances its cumulative cursor through `push`.

## Reproduce

Install the official Fe 26.5.0 compiler, then run from this directory:

```text
fe --version
fe test --backend sonatina --color never
fe test --backend sonatina --color never examples/collaborator_app
```

This source has been compiled and executed with `fe 26.5.0 (3dab95f)` on Windows using the Sonatina EVM test backend: 14 library tests and one separate importing-application test passed. The native test backend rejected Windows as unsupported; no native execution is claimed. No chain, wallet, key, token or mainnet deployment is needed for these tests.

`python demo/reference.py` prints an independently implemented exact-fraction example for 5:3:2 weights. This driver illustrates the schedule; it does not execute Fe.

## Mechanism

For each next unit, choose the recipient with the smallest exact ratio `(allocated_in_period + 1) / weight`, with stable recipient order breaking ties. This is the familiar D'Hondt/Jefferson highest-averages rule. Integer cross-products avoid floating-point comparisons. At a complete period equal to the sum of integer weights, every recipient has received exactly its weight. Whole periods can therefore be skipped before scanning the final partial period.

`allocate(weights, already, amount)` subtracts the prefix at `already` from the prefix at `already + amount`. The same fixed schedule makes batching irrelevant: a payment stream split into many calls has the same final result as one combined call. Up to eight recipients and a total weight of 10,000 are supported. The tail loop depends on that bounded total weight, not on the monetary amount.

The library uses checked u256 arithmetic and tests overflow rejection, max-u256 conservation, zero/excessive weights, fixed-series reweighting policy, partition invariance, one-unit receipts, and a non-clawback example. `Series.try_push(amount)` returns a `PushOutcome`; on cumulative overflow it returns `ok=false`, a zero allocation and an unchanged cursor. Its test rejects an excessive amount, checks the exact old cursor and then successfully accepts a valid amount. `push` retains its reverting API.

The two tail scans inspect at most `2 * 9999 * 8 = 159984` recipient slots. The exact maximum-tail input uses eight weights of 1250, `already=9999` and `amount=10000`. Its local execution time was 0.0656 seconds with the Sonatina backend, optimization default 1 and one job. That host measurement is not gas. The official runner lifts Osaka's transaction gas cap; passing it does not establish deployability at a chain's transaction limit. No low-gas or independent-security-audit claim is made.

Cross-products are bounded by the supported weight scale: each partial-period allocation is less than 10000, so the comparison products are at most 100,000,000. Each complete-period product `cycles * weight[i]` is bounded by `through`, and its final allocation is at most `through`. The cumulative sum is checked before `try_push` changes state. These bounds explain the arithmetic; finite examples are not presented as a formal proof.

## Choosing a policy

OpenZeppelin v4 PaymentSplitter is the closer payment comparison: its pending-payment formula uses cumulative receipts times shares, divided by total shares, minus prior releases. It already carries state across receipts. With eight units and weights 5:3:2, that cumulative-floor entitlement is `(4,2,1)` and one unit remains in the contract. CentWeave's corresponding prefix is `(5,2,1)` and no unit is left unassigned. At ten units both are `(5,3,2)`. The Fe test reproduces the entitlement arithmetic, not the Solidity contract's fund transfers.

Hamilton/largest remainder is a useful batch apportionment alternative, but cumulative allocations can fall when the total rises. Divisor methods avoid that particular problem. Deficit round robin and cumulative-error methods are other established ways to carry rounding state; this project does not claim to supersede them. D'Hondt can favor larger shares at small prefixes, and tie order matters. CentWeave makes that specific policy explicit and reproducible.

Recipient identities and weights must stay fixed within a series. A changed group starts a new `Series`; previous allocations remain in the old series. Restarting at zero changes the rounding schedule. The caller must retain the existing cursor and fixed recipient mapping; no durable storage or restart-neutrality guarantee is supplied. The caller is responsible for that boundary and for any actual funds, authorization, accounting or transfer mechanism. This is a calculation library, not a custody or payout contract.

`examples/collaborator_app` is a separate ingot with `centweave = { path = "../.." }`. Its test imports `centweave::Series`, pushes two receipts through the public API and verifies the combined eight-unit allocation. No unsafe trust flag or external dependency is needed.

## Sources

- OpenZeppelin v4.9.6 source, cumulative pending-payment formula: https://github.com/OpenZeppelin/openzeppelin-contracts/blob/v4.9.6/contracts/finance/PaymentSplitter.sol
- Fe 26.5 local dependencies and import syntax: https://fe-lang.org/ingots/dependencies/
- Fe test backend and lifted transaction gas cap: https://fe-lang.org/testing/runner/

## AI assistance

Codex was used for implementation, testing and documentation. ChatGPT reviewed the technical approach and claims.
