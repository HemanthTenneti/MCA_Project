# Live demonstration (5–7 minutes)

## Before presenting

Run `make all` once. It must exit successfully. Keep `reports/technical_report.md`
and `docs/design.md` open. Open `reports/results.html` for a visual comparison.
The shareable explanation is in `output/pdf/project_guide.pdf`. Prepare GTKWave with:

```sh
gtkwave reports/waveforms/two_bit.vcd docs/loop.gtkw
```

If GTKWave's macOS launcher is unavailable, use the delivered PNG waveform preview
and raw VCD with another waveform viewer. All verification is self-checking and
runs through Icarus; GTKWave is a visual inspection aid.

## Presentation sequence

1. **Problem (30 seconds):** a wrong next instruction address requires recovery.
   Explain direction versus target prediction using the architecture diagram.
2. **Baseline first (45 seconds):** show always-not-taken's `PC + 4` prediction.
   In the repeated loop, nine of each ten outcomes are taken: 288 recoveries.
3. **Learning (90 seconds):** run `make demo`. Show the first 12 predictions. Use `python3 scripts/demo.py --details`
   to show readable counter states and saved addresses.
   The 1-bit predictor misses loop exit and the next invocation's first branch.
   The 2-bit predictor keeps taken direction across a single loop exit.
4. **Waveform (60 seconds):** follow query-valid at issue N, saved-next-PC,
   update-valid at N+2, and flush/redirect. At the first cold branch the predicted
   next address is `0x104`; recovery redirects to `0x80`. Subsequent taken predictions
   use `0x80`. At the loop exit the actual next address becomes `0x104`.
5. **Honest comparison (60 seconds):** show the alternating workload, where both
   dynamic strategies lose, and BTB collisions, where direction accuracy is high
   but next-address accuracy is zero. Explain that the BHT and BTB solve different
   problems.
6. **Evidence (60 seconds):** show `reports/verification.json`, unit checks,
   synthesis CSV and gate-level checks. Explain the separate fixture reference and
   distinguish analytical CPI from measured CPU execution.

## Key numbers for the default repeated-loop trace

| Strategy | Next-PC correct | Recoveries | Estimated CPI |
|---|---:|---:|---:|
| Always not taken | 32 / 320 | 288 | 1.36000 |
| 1-bit | 256 / 320 | 64 | 1.08000 |
| 2-bit | 287 / 320 | 33 | 1.04125 |

There are 1,600 retired instructions and a two-cycle penalty. Two-bit therefore
has an estimated speedup of about 1.306x over baseline under this model.
These figures do not establish real processor throughput or a universal advantage.
