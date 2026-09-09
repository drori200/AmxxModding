#!/usr/bin/env python3
"""AMXX research entry point. PAWN advancement is a prerequisite."""
from pawn_gate import require_current_pass


def main():
    # This must precede discovery, downloads, compiler calls, or server actions.
    require_current_pass()
    raise SystemExit("PAWN gate accepted. AMXX lab implementation is still pending; no runtime claim is available.")


if __name__ == "__main__":
    main()
