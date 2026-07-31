# SolarScan landing-page content contract

This file records the claims that the public landing page may make. It exists so copy,
tests, and implementation can be reviewed against the same evidence.

## Audience and job

- Primary audience: solar pre-sales engineers and technical users doing early rooftop triage.
- Secondary audience: portfolio analysts who want one consistent report per address.
- Core job: turn a location into an inspectable first-pass roof, capacity, yield, payback,
  and PDF estimate before detailed design begins.

## Supported paths

```text
git clone https://github.com/IamOumarIbrahim/SolarScan.git
cd SolarScan
python -m pip install -e .
solarscan scan "Computer Science Department W5 Sharjah"
```

The packaged Windows installer is attached to release `v0.5.0` as
`SolarScan_Setup_v0.5.0.exe`. Adding SolarScan to `PATH` is an installer task the user
must select.

## W5 case-study facts

| Measure | Value |
| --- | ---: |
| Manual Google Earth trace | 1,699.86 m² |
| Retrieved OSM footprint | 1,610.02 m² |
| OSM/manual area ratio | 94.7% |
| Relative area difference | 5.3% |
| Perimeter used by the engine | 165.40 m |
| Usable area at 1.50 m setback | 1,361.92 m² |
| DC estimate at 20% module efficiency | 272.38 kW |
| AC estimate at 1.20 DC/AC | 226.99 kW |
| Annual yield with current defaults | approximately 232,395 kWh/year |
| Simple payback at 0.38/kWh and 1,000/kW | 3.08 years |

The 94.7% figure is an area ratio for one comparison. It is not a general accuracy,
agreement, energy-yield, or system-performance score.

## Required boundary language

- The OSM query and browser fixture are not a site survey.
- The setback calculation is `max(0, A - perimeter × setback - obstruction area)`.
  It is not a geometric polygon inset or a fire-code layout.
- The current query does not extract rooftop obstructions.
- Shading, roof pitch, structural capacity, clearances, code compliance, interconnection,
  and bankable energy modeling are outside the current engine.
- The Python engine uses a synthetic polygon after all Overpass mirrors fail. That output
  must be treated as a fallback/error condition, not a measured building.
