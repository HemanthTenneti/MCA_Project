"""Sequential architectural oracle, independent of Verilog implementation."""
from dataclasses import dataclass, field

MASK = (1 << 32) - 1


@dataclass
class Predictor:
    mode: int
    bht_bits: int = 6
    btb_bits: int = 4
    counters: list = field(init=False)
    targets: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.mode not in (0, 1, 2):
            raise ValueError('mode must be 0, 1, or 2')
        self.counters = [int(self.mode == 2)] * (1 << self.bht_bits)

    def step(self, b):
        pc, target, taken = b['pc'], b['target'], b['taken']
        # Integer division/modulo rather than duplicating RTL slices.
        index = (pc // 4) % len(self.counters)
        state = self.counters[index] if self.mode else 0
        predicted = int(state >= (2 if self.mode == 2 else 1)) if self.mode else 0
        slot = (pc // 4) % (1 << self.btb_bits)
        entry = self.targets.get(slot)
        hit = int(entry is not None and entry[0] == pc)
        next_pc = entry[1] if predicted and hit else (pc + 4) & MASK
        actual_next = target if taken else (pc + 4) & MASK
        result = dict(pc=pc, state=state, predicted_taken=predicted, btb_hit=hit,
                      predicted_next_pc=next_pc, actual_next_pc=actual_next,
                      flush=int(next_pc != actual_next))
        if self.mode == 1:
            self.counters[index] = taken
        elif self.mode == 2:
            self.counters[index] = max(0, min(3, state + (1 if taken else -1)))
        if taken:
            self.targets[slot] = (pc, target)
        return result
