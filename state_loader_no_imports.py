class State:
    """A lightweight container mapping CSV headers to attributes.

    Constructor: State(header_list, row_list)
    """
    def __init__(self, header, row):
        # normalize row length
        if len(row) < len(header):
            row = row + [""] * (len(header) - len(row))
        elif len(row) > len(header):
            row = row[:len(header)]

        for k, v in zip(header, row):
            val = self._convert(v, k)
            setattr(self, k.strip(), val)

    def _convert(self, s, key_name):
        if s is None:
            return None
        s2 = s.strip()
        if s2 == "":
            return None
        lower_key = key_name.lower()
        if lower_key in ("fips", "hash", "totaltestresultssource", "dataqualitygrade", "grade", "state", "lastupdateet", "checktimeet"):
            return s2
        # remove commas from numbers like "1,234"
        if "," in s2:
            s3 = s2.replace(",", "")
            if self._looks_like_int(s3):
                try:
                    return int(s3)
                except Exception:
                    pass
        if self._looks_like_int(s2):
            try:
                return int(s2)
            except Exception:
                pass
        # try float only when a decimal point is present
        try:
            if "." in s2:
                return float(s2)
        except Exception:
            pass
        return s2

    def _looks_like_int(self, s):
        if not s:
            return False
        if s[0] in ('-', '+'):
            return s[1:].isdigit()
        return s.isdigit()

    def as_dict(self):
        d = {}
        for k, v in self.__dict__.items():
            d[k] = v
        return d

    def __repr__(self):
        return "State(state=%r, date=%r, positive=%r)" % (getattr(self, 'state', None), getattr(self, 'date', None), getattr(self, 'positive', None))


# Simple CSV line parser that supports quoted fields with commas and escaped quotes.
# This is intentionally minimal and should handle the majority of well-formed CSVs.

def parse_csv_line(line):
    fields = []
    cur = []
    in_quotes = False
    i = 0
    while i < len(line):
        ch = line[i]
        if in_quotes:
            if ch == '"':
                # lookahead for escaped quote
                if i + 1 < len(line) and line[i+1] == '"':
                    cur.append('"')
                    i += 1
                else:
                    in_quotes = False
            else:
                cur.append(ch)
        else:
            if ch == ',':
                fields.append(''.join(cur))
                cur = []
            elif ch == '"':
                in_quotes = True
            else:
                cur.append(ch)
        i += 1
    fields.append(''.join(cur))
    return fields


def load_states_no_imports(path):
    states = []
    with open(path, 'r', encoding='utf-8') as fh:
        # read header
        first = fh.readline()
        if not first:
            return states
        header = parse_csv_line(first.rstrip('\n\r'))
        header = [h.strip() for h in header]
        for line in fh:
            line = line.rstrip('\n\r')
            if not line:
                continue
            row = parse_csv_line(line)
            states.append(State(header, row))
    return states


def main(argv=None):
    # This function intentionally avoids using sys.argv or any imports.
    # It will auto-load a sensible default CSV file path unless an argv list
    # with a path is provided programmatically.
    default_path = r'c:\Users\camjh\Downloads\extracted_files\usscv19d.csv'
    if argv and len(argv) > 0 and argv[0]:
        path = argv[0]
    else:
        path = default_path

    print('Loading', path)
    try:
        states = load_states_no_imports(path)
    except Exception as e:
        print('Error loading file:', e)
        return 2

    print('Loaded %d rows' % len(states))

    # Build an index of states -> list of State objects
    groups = {}
    for s in states:
        code = getattr(s, 'state', None)
        if code is None:
            continue
        groups.setdefault(code.upper(), []).append(s)

    # try to sort each group's rows by a numeric date if present
    for code, rows in groups.items():
        try:
            rows.sort(key=lambda x: (getattr(x, 'date', None) or 0))
        except Exception:
            pass

    # Interactive loop: ask for a state code and show attributes
    print('\nEnter a 2-letter state code to display its rows, or:')
    print("  'all' to list available state codes and counts, 'quit' to exit")
    while True:
        try:
            choice = input('\nState code (or all/quit): ').strip()
        except Exception:
            print('\nInput error; exiting.')
            break
        if not choice:
            continue
        c = choice.strip().upper()
        if c == 'QUIT' or c == 'EXIT':
            print('Goodbye')
            break
        if c == 'ALL':
            # show codes and counts
            codes = sorted(groups.keys())
            for code in codes:
                print('%s: %d rows' % (code, len(groups[code])))
            continue
        if c not in groups:
            print('No data for state code:', c)
            # helpful suggestion: show nearest matches (prefix)
            suggestions = [k for k in groups.keys() if k.startswith(c[:1])]
            if suggestions:
                print('Did you mean:', ', '.join(suggestions[:8]))
            continue

        # print all rows for this state
        rows = groups[c]
        print('\nShowing %d rows for %s' % (len(rows), c))
        for idx, row in enumerate(rows, 1):
            print('\n--- row %d ---' % idx)
            d = row.as_dict()
            # print attributes in a stable order
            keys = sorted(d.keys())
            for k in keys:
                print('  %s: %r' % (k, d[k]))
    
    return 0


if __name__ == '__main__':
    # Run interactively; main() will prompt if no argv passed.
    main()
