import sys

def fmt_addresses(filename):
    f = open(filename)
    addresses = []
    for line in f:
        addresses.append(fmt_address(line))
    return addresses

def fmt_address(address_str):

    address_str = format_input_address(address_str)
    if len(address_str) == 0: return ''

    address_list = parse_address(address_str)
    return '|'.join(address_list)

def format_input_address(address_str):
    address_str = address_str.strip()
    trim_index = address_str.find(" US")

    if trim_index == -1: trim_index = address_str.find("TN0")
    if trim_index > -1: address_str = address_str[0:trim_index]
    return address_str

def parse_address(address_str):
    split = address_str.split(',')
    split = [string.strip() for string in split]
    split2 = split[-1].split(' ')
    if len(split2) > 3:
        street_name = split[0] + ', ' + ' '.join(split2[0:len(split2)-3])
    else:
        street_name = ' '.join(split[0:len(split)-1])

    loc_info = split2[len(split2)-3:]
    if len(loc_info) > 2: loc_info[2] = loc_info[2].split('-')[0]
    return [street_name] + loc_info

def main(filename):
    addresses = fmt_addresses(filename)
    print '\n'.join(addresses)

if __name__ == "__main__":
    main(sys.argv[1])
