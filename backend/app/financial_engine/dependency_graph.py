"""
Transaction dependency graph — ordered ledger chain for balance propagation.
"""

from __future__ import annotations

from decimal import Decimal

from app.financial_engine.models import DependencyGraph, LedgerEntry, TransactionNode


def build_dependency_graph(
    entries: list[LedgerEntry],
    opening_balance: Decimal | None = None,
) -> DependencyGraph:
    nodes: list[TransactionNode] = []
    sorted_entries = sorted(entries, key=lambda e: (e.page, e.row_index))

    for i, entry in enumerate(sorted_entries):
        prev_id = sorted_entries[i - 1].transaction_id if i > 0 else None
        next_id = sorted_entries[i + 1].transaction_id if i < len(sorted_entries) - 1 else None
        nodes.append(
            TransactionNode(
                transaction_id=entry.transaction_id,
                index=i,
                previous_id=prev_id,
                next_id=next_id,
            )
        )

    return DependencyGraph(nodes=nodes, opening_balance=opening_balance)


def index_of(graph: DependencyGraph, transaction_id: str) -> int:
    for node in graph.nodes:
        if node.transaction_id == transaction_id:
            return node.index
    raise KeyError(f"Transaction not in graph: {transaction_id}")


def downstream_ids(graph: DependencyGraph, from_index: int) -> list[str]:
    return [n.transaction_id for n in graph.nodes if n.index >= from_index]
