"""Independent Python example driver; Fe is the judged implementation.

Exact Fraction priority ordering makes the correspondence with D'Hondt visible.
This file does not execute Fe and must not be presented as compiler evidence.
"""
from fractions import Fraction


def prefix(weights, total):
    if not 1 <= sum(weights) <= 10000 or any(type(x) is not int or x < 0 for x in weights):
        raise ValueError("invalid weights")
    q,r=divmod(total,sum(weights))
    small=[0]*len(weights)
    for _ in range(r):
        winner=min((i for i,w in enumerate(weights) if w),key=lambda i:(Fraction(small[i]+1,weights[i]),i))
        small[winner]+=1
    return [q*w+s for w,s in zip(weights,small)]


if __name__ == "__main__":
    import json
    weights=[5,3,2]
    result={"weights":weights,"example_only":True,"receipts":[]}
    last=[0,0,0]
    for t in range(1,11):
        now=prefix(weights,t)
        result["receipts"].append({"receipt_unit":t,"this_receipt":[n-l for n,l in zip(now,last)],"cumulative":now})
        last=now
    print(json.dumps(result,indent=2))
