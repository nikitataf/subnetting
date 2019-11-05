__author__ = 'Tafintsev Nikita'

import math
import copy


class Calculator(object):

    def __init__(self):
        self.buff = []

    def parse(self, address):
        address = address.partition(' /')
        add = address[0]
        print('IP address:', add)
        bitmask = int(address[2])
        #print('Netmask:', self.bitmask)
        ip = add.split('.')
        if len(ip) > 4:
            raise ValueError('%s: IPv4 address invalid: '
                             'more than 4 bytes' % add)
        for x in ip:
            if not 0 <= int(x) <= 255:
                raise ValueError('%s: IPv4 address invalid: '
                                 'bytes should be between 0 and 255' % add)
        netmask = '1' * bitmask + '0' * (32 - bitmask)
        #print('Binary netmask:', netmask)
        octet = [netmask[0:8], netmask[8:16], netmask[16:24], netmask[24:32]]

        mask = []
        for i in range(len(octet)):
            dec = int(octet[i], 2)
            mask.append(dec)
        print("Netmask:", bitmask, "-" , ".".join(map(str, mask)))

        netwildcard = '0' * bitmask + '1' * (32 - bitmask)
        octet_wildcard = [netwildcard[0:8], netwildcard[8:16], netwildcard[16:24], netwildcard[24:32]]
        wildcard = []
        for i in range(len(octet_wildcard)):
            dec = int(octet_wildcard[i], 2)
            wildcard.append(dec)
        print("Wildcard:", ".".join(map(str, wildcard)))

        net_add = []
        for p in range(len(ip)):
            a = int(ip[p])
            b = int(octet[p], 2)
            net_add.append(a & b)
        print("Network address:", ".".join(map(str, net_add)))

        broadcast_add = []
        octet_inv = [netwildcard[0:8], netwildcard[8:16], netwildcard[16:24], netwildcard[24:32]]
        for p in range(len(net_add)):
            a = int(net_add[p])
            b = int(octet_inv[p], 2)
            broadcast_add.append(a | b)
        print("Broadcast address:", ".".join(map(str, broadcast_add)))

        hostmin = net_add
        hostmin[3] += 1
        hostmin_str = ".".join(map(str, hostmin))
        print("Hostmin address:", hostmin_str)

        hostmax = broadcast_add
        hostmax[3] -= 1
        hostmax_str = ".".join(map(str, hostmax))
        print("Hostmax address:", hostmax_str)

        print("Network range:", hostmin_str, "-", hostmax_str)

        total = hostmax[3] - hostmin[3] + 1
        print("Total hosts:", total)

    def subnet(self, input):
        address = input.partition('divide')
        add = address[0]
        net_add = add.partition(' /')
        ip = net_add[0]
        bitmask = int(net_add[2])
        ip = ip.split('.')
        netmask = '1' * bitmask + '0' * (32 - bitmask)
        octet = [netmask[0:8], netmask[8:16], netmask[16:24], netmask[24:32]]

        net_add = []
        for p in range(len(ip)):
            a = int(ip[p])
            b = int(octet[p], 2)
            net_add.append(a & b)

        count = int(address[2])
        d = int(math.log(count, 2))
        target = bitmask + d
        move = math.ceil(target / 8.0)
        host = (move * 8) - target
        jump = 2 ** host
        self.buff = copy.deepcopy(net_add)
        print("Subnet", add,"is splitted into", count, "parts:")
        for i in range(count):
            print("#", i + 1, ".".join(map(str, self.buff)), '/', target)
            self._add(move, jump)
        print("Every subnet has", 2 ** (32 - target) - 2,"usable IP addresses")

    def _add(self, octet, value):
        octet = int(octet)
        self.buff[octet - 1] = self.buff[octet - 1] + int(value)
        for i in range(octet - 1, -1, -1):
            if self.buff[i] >= 256:
                self.buff[i] = 0
                self.buff[i - 1] = self.buff[i - 1] + 1

    def _dqtoi(self, dq):
        q = dq.split('.')
        q.reverse()
        while len(q) < 4:
            q.insert(1, '0')
        return sum(int(byte) << 8 * index for index, byte in enumerate(q))

    def _itodq(self, n):
        return '.'.join(map(str, [
            (n >> 24) & 0xff,
            (n >> 16) & 0xff,
            (n >> 8) & 0xff,
            n & 0xff,]))

    def _borders(self, address, mask):
        max = (1 << 32) - 1
        ip = self._dqtoi(address)
        netmask = (max >> (32 - mask)) << (32 - mask)
        network = ip & netmask
        broadcast = network | (max - netmask)
        return network, broadcast

    def merge(self, input):
        addresses = input.partition(' plus')
        address_1 = addresses[0]
        address_1 = address_1.partition(' /')
        ip_1 = address_1[0]
        bitmask_1 = int(address_1[2])
        address_2 = addresses[2]
        address_2 = address_2.partition(' /')
        ip_2 = address_2[0]
        bitmask_2 = int(address_2[2])

        params_1 = self._borders(ip_1, bitmask_1)
        params_2 = self._borders(ip_2, bitmask_2)
        ranges = [[params_1[0], params_1[1]], [params_2[0], params_2[1]]]
        ranges.sort()
        borders = []
        if ranges[1][0] - 1 <= ranges[0][1]:
            borders = (ranges[1][1], min(ranges[0][0], ranges[1][0]))
        lowest_ipnum = borders[1]
        ipnum = borders[0]
        prefixlen= 32
        while prefixlen > 0 and ipnum > lowest_ipnum:
            prefixlen -= 1
            ipnum &= -(1 << (32 - prefixlen))
        addr = self._itodq(ipnum)
        print("Result:", addr, "/", prefixlen)


if __name__ == "__main__":
    calc = Calculator()
    calc.parse('192.168.0.15 /24')
    calc.subnet('10.0.0.0 /16 divide 4')
    calc.merge('10.0.0.0 /25 plus 10.0.0.128 /25')
