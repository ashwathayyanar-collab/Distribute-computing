import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from lamport import LamportSimulator, simulate


def test_rejects_too_few_processes():
    with pytest.raises(ValueError):
        LamportSimulator(num_processes=1)


def test_rejects_invalid_probability():
    with pytest.raises(ValueError):
        LamportSimulator(num_processes=3, message_probability=1.5)


def test_clocks_only_increase_within_a_process():
    result = simulate(num_processes=4, events_per_process=10, seed=42)
    for timeline in result["timelines"]:
        clocks = [e["clock"] for e in timeline]
        assert clocks == sorted(clocks), "clock values must be non-decreasing per process"
        assert len(set(clocks)) == len(clocks), "clock values must strictly increase per process"


def test_receive_clock_exceeds_send_clock():
    """Lamport's rule L2: receiver's clock must be > the timestamp carried by the message."""
    result = simulate(num_processes=3, events_per_process=8, message_probability=0.6, seed=7)
    for m in result["messages"]:
        assert m["recv_clock"] is not None, "every sent message must eventually be received"
        assert m["recv_clock"] > m["send_clock"]


def test_every_message_has_matching_send_and_receive_events():
    result = simulate(num_processes=3, events_per_process=8, message_probability=0.6, seed=7)
    for m in result["messages"]:
        send_events = [e for e in result["timelines"][m["from"]]
                       if e["kind"] == "send" and e["message_id"] == m["id"]]
        recv_events = [e for e in result["timelines"][m["to"]]
                       if e["kind"] == "receive" and e["message_id"] == m["id"]]
        assert len(send_events) == 1
        assert len(recv_events) == 1


def test_deterministic_with_seed():
    a = simulate(num_processes=3, events_per_process=6, seed=123)
    b = simulate(num_processes=3, events_per_process=6, seed=123)
    assert a == b


def test_final_clocks_match_last_event_per_process():
    result = simulate(num_processes=3, events_per_process=6, seed=1)
    for p, timeline in enumerate(result["timelines"]):
        assert result["final_clocks"][p] == timeline[-1]["clock"]


def test_event_count_per_process():
    result = simulate(num_processes=3, events_per_process=5, seed=99)
    for timeline in result["timelines"]:
        # events_per_process "own steps" plus possibly extra receives flushed at the end
        assert len(timeline) >= 5
