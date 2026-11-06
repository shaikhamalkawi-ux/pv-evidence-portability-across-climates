#!/usr/bin/env python3
"""Audit nominal shortlist transfer from a positive-endpoint CSV.

The input has one row per module and a named column for each site. This implements
only the paper's existing deficit and half-open exclusion-interval definitions.
It is not a measurement-uncertainty certificate, optimizer or empirical validation.
Uses the standard library; fraction arithmetic preserves exact threshold equality.
"""
from __future__ import annotations
import argparse, csv, json, os, sys, tempfile
from fractions import Fraction
from pathlib import Path

def positive(value: str, label: str) -> Fraction:
    try:
        result = Fraction(value.strip())
    except (ValueError, ZeroDivisionError, AttributeError) as exc:
        raise ValueError(f'Invalid finite numeric endpoint for {label}: {value!r}') from exc
    if result <= 0:
        raise ValueError(f'Endpoint must be strictly positive for {label}.')
    return result

def load(path: Path, source: str, target: str, exclude: set[str]):
    if source == target or 'module' in (source, target):
        raise ValueError('Source and target must be distinct endpoint columns, not module.')
    with path.open(newline='', encoding='utf-8-sig') as stream:
        reader = csv.reader(stream, strict=True)
        headers = next(reader, None)
        if (not headers or any(not name or name != name.strip() for name in headers)
                or len(set(headers)) != len(headers)):
            raise ValueError('Missing, blank, padded or duplicate CSV column names.')
        if not {'module', source, target}.issubset(headers):
            raise ValueError('CSV must contain module plus both site columns.')
        result = {}; seen = set()
        for values in reader:
            if not values:  # Ignore empty physical lines, as csv.DictReader did.
                continue
            if len(values) != len(headers):
                raise ValueError(f'CSV record ending on line {reader.line_num} has '
                                 f'{len(values)} fields; expected {len(headers)}.')
            row = dict(zip(headers, values))
            name = row['module'].strip()
            if not name or name in seen:
                raise ValueError('Blank or duplicate module identifier.')
            seen.add(name)
            a = positive(row[source], f'{name}/{source}')
            b = positive(row[target], f'{name}/{target}')
            if name not in exclude:
                result[name] = (a, b)
        unknown = exclude - seen
        if unknown:
            raise ValueError('Excluded identifiers absent from input: ' + ', '.join(sorted(unknown)))
        if not result:
            raise ValueError('No modules remain in the declared cohort.')
    return result

def evaluate(data: dict[str, tuple[Fraction,Fraction]], q: Fraction):
    if q<0:
        raise ValueError('q must be nonnegative.')
    if not data or any(a<=0 or b<=0 for a,b in data.values()):
        raise ValueError('Cohort must be nonempty with positive endpoints.')
    maxima=(max(v[0] for v in data.values()),max(v[1] for v in data.values()))
    deficits={name:(100*(1-v[0]/maxima[0]),100*(1-v[1]/maxima[1])) for name,v in data.items()}
    source_set={name for name,d in deficits.items() if d[0]<=q}
    target_set={name for name,d in deficits.items() if d[1]<=q}
    exclusions=sorted(target_set-source_set)
    intervals=[]
    for name,(ds,dt) in sorted(deficits.items()):
        if dt<ds:
            intervals.append({'module':name,'q_low_inclusive_pct':float(dt),
                 'q_high_exclusive_pct':float(ds),'q_low_exact':str(dt),'q_high_exact':str(ds)})
    return {'cohort_size':len(data),'q_percentage_points':float(q),
        'source_best_endpoint':float(maxima[0]),'target_best_endpoint':float(maxima[1]),
        'source_shortlist':sorted(source_set),'target_shortlist':sorted(target_set),
        'false_exclusions':exclusions,'false_exclusion_count':len(exclusions),
        'excess_retentions':sorted(source_set-target_set),
        'target_retained_count':len(target_set),
        'target_set_coverage_pct':100*len(target_set & source_set)/len(target_set),
        'nominal_false_exclusion_intervals':intervals,
        'deficits':{n:{'source_pct':float(d[0]),'target_pct':float(d[1])} for n,d in sorted(deficits.items())},
        'interpretation':'nominal point-estimate set comparison; no uncertainty-calibrated guarantee'}

def protect_input_path(source: Path, output: Path) -> None:
    """Refuse path aliases that would replace the caller's input file."""
    if source.resolve() == output.resolve():
        raise ValueError('Output must be a different file from input.')
    if source.exists() and output.exists() and source.samefile(output):
        raise ValueError('Output is a filesystem alias of input.')
    if output.is_symlink():
        raise ValueError('Output must not be a symbolic link.')


def write_json_atomic(output: Path, result: dict) -> None:
    """Serialize before writing, then replace only the intended result file."""
    text = json.dumps(result, indent=2, allow_nan=False) + '\n'
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', newline='\n',
                                         dir=output.parent, prefix='.shortlist-',
                                         suffix='.tmp', delete=False) as stream:
            temporary = Path(stream.name)
            stream.write(text)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, output)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--source',required=True);p.add_argument('--target',required=True)
    p.add_argument('--q',default='5',help='Nonnegative deficit cutoff in percentage points.')
    p.add_argument('--exclude',action='append',default=[],help='Repeat for each explicitly excluded module.')
    p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    protect_input_path(a.input, a.output)
    try:q=Fraction(a.q)
    except (ValueError,ZeroDivisionError) as exc:raise ValueError('q must be a finite number.') from exc
    r=evaluate(load(a.input,a.source,a.target,set(a.exclude)),q)
    r.update(source=a.source,target=a.target,excluded_modules=sorted(set(a.exclude)))
    protect_input_path(a.input, a.output)
    write_json_atomic(a.output, r)
    print(f'{a.source} -> {a.target}: {r["false_exclusion_count"]}/{r["target_retained_count"]} nominal exclusions')
if __name__=='__main__':
    try:main()
    except (ValueError,OSError,csv.Error,UnicodeError,OverflowError) as e:
        print(f'INPUT REJECTED: {e}',file=sys.stderr);raise SystemExit(2)
