#!/usr/bin/env python3
import argparse


def main():
    p = argparse.ArgumentParser(description="Simulate post-borrow health")
    p.add_argument("--weighted-collateral", type=float, required=True)
    p.add_argument("--current-debt", type=float, required=True)
    p.add_argument("--extra-borrow", type=float, required=True)
    args = p.parse_args()

    new_debt = args.current_debt + args.extra_borrow
    if new_debt <= 0:
        print("post_health=inf")
        return

    post_health = args.weighted_collateral / new_debt
    print(f"post_health={post_health:.4f}")


if __name__ == "__main__":
    main()
