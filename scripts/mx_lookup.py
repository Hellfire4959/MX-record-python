"""Export DNS MX records for domains in an Excel workbook."""
import argparse
from pathlib import Path
import sys
import dns.exception
import dns.resolver
import pandas as pd

def get_mx_records(domain, resolver=None):
    resolver = resolver if resolver is not None else dns.resolver.Resolver()
    try:
        lookup = domain.strip().rstrip('.').encode('idna').decode('ascii')
        answers = sorted(resolver.resolve(lookup, 'MX'), key=lambda record: record.preference)
        hosts = [record.exchange.to_text().rstrip('.') for record in answers]
        preferences = [str(record.preference) for record in answers]
        null_mx = len(answers) == 1 and answers[0].preference == 0 and answers[0].exchange.to_text() == '.'
        return {'Domain': domain, 'MX_Found': 'Null MX' if null_mx else 'Yes',
                'MX_Records': '0 .' if null_mx else '; '.join(hosts),
                'Preferences': '; '.join(preferences),
                'Primary_Host': 'N/A' if null_mx or not hosts else hosts[0], 'Error': ''}
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return {'Domain':domain, 'MX_Found':'No', 'MX_Records':'', 'Preferences':'', 'Primary_Host':'N/A', 'Error':''}
    except (dns.exception.DNSException, UnicodeError, ValueError) as error:
        return {'Domain':domain, 'MX_Found':'Error', 'MX_Records':'', 'Preferences':'', 'Primary_Host':'N/A', 'Error':type(error).__name__}

def audit(input_file, output_file, resolver=None):
    if Path(input_file).resolve() == Path(output_file).resolve():
        raise ValueError('Input and output paths must be different.')
    data = pd.read_excel(input_file, keep_default_na=False)
    if 'Domain' not in data.columns: raise ValueError('Input worksheet must have a Domain column.')
    rows = []
    for value in data['Domain']:
        domain = str(value).strip()
        rows.append(get_mx_records(domain, resolver) if domain else {'Domain':'', 'MX_Found':'Blank',
            'MX_Records':'', 'Preferences':'', 'Primary_Host':'N/A', 'Error':''})
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows,columns=['Domain','MX_Found','MX_Records','Preferences','Primary_Host','Error']).to_excel(output_file,index=False)
    return len(rows)

def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input_file', type=Path, help='Excel workbook with a Domain column.')
    parser.add_argument('output_file', type=Path, help='Output .xlsx workbook.')
    args = parser.parse_args(argv)
    if args.output_file.suffix.lower() != '.xlsx': parser.error('output_file must end in .xlsx')
    resolver = dns.resolver.Resolver(); resolver.lifetime = 5
    try: rows = audit(args.input_file,args.output_file,resolver)
    except (OSError,ValueError) as error:
        print(f'Error: {error}',file=sys.stderr); return 1
    print(f'Wrote {rows} rows to {args.output_file}'); return 0

if __name__ == '__main__': sys.exit(main())
