#!/usr/bin/env python3
"""Compatibility wrapper for the reusable price pipeline sample mode."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import price_pipeline


if __name__ == "__main__":
    sys.argv = [sys.argv[0], "--mode", "sample", *sys.argv[1:]]
    price_pipeline.main()
