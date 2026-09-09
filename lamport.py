"""
Lamport Logical Clock simulation engine.

Implements the two rules of Lamport's logical clocks (1978):
  L1: A process increments its own clock before each event.
  L2: On receiving a message with timestamp T, a process sets its
      clock to max(local_clock, T) + 1.

The engine generates a randomized (but seedable) schedule of
INTERNAL, SEND, and RECEIVE events across N processes and returns
a JSON-serializable trace that the frontend renders as a timeline.
"""

import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional


@dataclass
class Event:
    process: int
    seq: int          # order of this event within its own process
    kind: str         # "internal" | "send" | "receive"
    clock: int
    message_id: Optional[int] = None  # links a send to its receive

    def to_dict(self) -> Dict:
        return {
            "process": self.process,
            "seq": self.seq,
            "kind": self.kind,
            "clock": self.clock,
            "message_id": self.message_id,
        }


class LamportSimulator:
    def __init__(self, num_processes: int = 3, events_per_process: int = 6,
                 message_probability: float = 0.35, seed: Optional[int] = None):
        if num_processes < 2:
            raise ValueError("num_processes must be at least 2")
        if events_per_process < 1:
            raise ValueError("events_per_process must be at least 1")
        if not (0 <= message_probability <= 1):
            raise ValueError("message_probability must be between 0 and 1")

        self.num_processes = num_processes
        self.events_per_process = events_per_process
        self.message_probability = message_probability
        self.rng = random.Random(seed)

        self.clocks = [0] * num_processes
        self.timelines: List[List[Event]] = [[] for _ in range(num_processes)]
        # pending[p] = list of (message_id, clock_at_send) sent to p, not yet delivered
        self.pending: Dict[int, List[Dict]] = {p: [] for p in range(num_processes)}
        self._next_message_id = 0

    def _tick(self, p: int) -> int:
        self.clocks[p] += 1
        return self.clocks[p]

    def _record(self, p: int, kind: str, message_id: Optional[int] = None) -> Event:
        clock = self._tick(p)
        ev = Event(process=p, seq=len(self.timelines[p]), kind=kind,
                   clock=clock, message_id=message_id)
        self.timelines[p].append(ev)
        return ev

    def run(self) -> Dict:
        messages = []  # {"id", "from", "to", "send_clock", "recv_clock"}

        for step in range(self.events_per_process):
            for p in range(self.num_processes):
                # Deliver one pending message for this process before its own step,
                # if one is waiting and a coin flip says "deliver now".
                if self.pending[p] and self.rng.random() < 0.5:
                    msg = self.pending[p].pop(0)
                    self.clocks[p] = max(self.clocks[p], msg["send_clock"])
                    ev = self._record(p, "receive", message_id=msg["id"])
                    for m in messages:
                        if m["id"] == msg["id"]:
                            m["recv_clock"] = ev.clock
                            break
                    continue

                # Otherwise decide: send a message, or a plain internal event.
                other_candidates = [q for q in range(self.num_processes) if q != p]
                if other_candidates and self.rng.random() < self.message_probability:
                    target = self.rng.choice(other_candidates)
                    ev = self._record(p, "send", message_id=self._next_message_id)
                    messages.append({
                        "id": self._next_message_id,
                        "from": p,
                        "to": target,
                        "send_clock": ev.clock,
                        "recv_clock": None,
                    })
                    self.pending[target].append({
                        "id": self._next_message_id,
                        "send_clock": ev.clock,
                    })
                    self._next_message_id += 1
                else:
                    self._record(p, "internal")

        # Flush any messages still pending (deliver at the end).
        for p in range(self.num_processes):
            while self.pending[p]:
                msg = self.pending[p].pop(0)
                self.clocks[p] = max(self.clocks[p], msg["send_clock"])
                ev = self._record(p, "receive", message_id=msg["id"])
                for m in messages:
                    if m["id"] == msg["id"]:
                        m["recv_clock"] = ev.clock
                        break

        return {
            "num_processes": self.num_processes,
            "timelines": [[e.to_dict() for e in tl] for tl in self.timelines],
            "messages": messages,
            "final_clocks": list(self.clocks),
        }


def simulate(num_processes: int = 3, events_per_process: int = 6,
             message_probability: float = 0.35, seed: Optional[int] = None) -> Dict:
    sim = LamportSimulator(num_processes, events_per_process, message_probability, seed)
    return sim.run()
