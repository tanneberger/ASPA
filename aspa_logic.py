
IPv4, IPv6 = 4, 6
AS_SET, AS_SEQUENCE, AS_CONFED_SEQUENCE, AS_CONFED_SET = range(1, 5)
Valid, Invalid, Unknown, Unverifiable = range(4)


class Segment:
    def __init__(self, value, type):
        self.value, self.type = value, type


class ASPA:
    def __init__(self, aspa_records):
        self.aspa_records = aspa_records

    def verify_pair(self, as1, as2, afi):
        aspa_records_afi = self.aspa_records.get(afi, None)
        if aspa_records_afi is None:
            return Unknown

        aspa_records_as1 = aspa_records_afi.get(as1, None)
        if aspa_records_as1 is None:
            return Unknown

        if as2 not in aspa_records_as1:
            return Invalid
        return Valid

    def check_upflow_path(self, aspath, neighbor_as, afi):
        if len(aspath) == 0:
            return Invalid

        if aspath[-1].type == AS_SEQUENCE and aspath[-1].value != neighbor_as:
            return Invalid

        semi_state = Valid

        as1 = 0
        for segment in aspath:
            if segment.type != AS_SEQUENCE:
                as1 = 0
                semi_state = Unverifiable
            elif segment.type == AS_SEQUENCE:
                if not as1:
                    as1 = segment.value
                elif as1 != segment.value:
                    pair_check = self.verify_pair(as1, segment.value, afi)
                    if pair_check == Invalid:
                        return Invalid
                    elif pair_check == Unknown and semi_state == Valid:
                        semi_state = pair_check
                    as1 = segment.value
        return semi_state

    def check_downflow_path(self, aspath, neighbor_as, afi):
        def get_indexes(aspath, afi):
            unknown_index = 0
            unverifiable_flag = False

            as1 = 0
            index = 0
            for segment in aspath:
                if segment.type != AS_SEQUENCE:
                    as1 = 0
                    unverifiable_flag = True
                elif segment.type == AS_SEQUENCE:
                    if not as1:
                        as1 = segment.value
                    elif as1 != segment.value:
                        pair_check = self.verify_pair(as1, segment.value, afi)
                        if pair_check == Invalid:
                            return index, unknown_index if unknown_index else index, unverifiable_flag
                        elif pair_check == Unknown and not unknown_index:
                            unknown_index = index

                        as1 = segment.value

                index += 1

            return index, unknown_index if unknown_index else index, unverifiable_flag

        if len(aspath) == 0:
            return Invalid

        if aspath[-1].type == AS_SEQUENCE and aspath[-1].value != neighbor_as:
            return Invalid

        forward_invalid_index, forward_unknown_index, forward_unverifiable = get_indexes(aspath, afi)
        backward_invalid_index, backward_unknown_index, backward_unverifiable = get_indexes(list(reversed(aspath)), afi)

        aspath_len = len(aspath)
        if forward_invalid_index + backward_invalid_index < aspath_len:
            return Invalid
        if forward_unverifiable or backward_unverifiable:
            return Unverifiable
        if forward_unknown_index + backward_unknown_index < aspath_len:
            return Unknown
        return Valid

    def check_ix_path(self, aspath, neighbor_as, afi):
        if len(aspath) == 0:
            return Invalid
        if len(aspath) == 0:
            return Invalid

        if aspath[-1].value != neighbor_as:
            return self.check_upflow_path(aspath, aspath[-1].value, afi)
        else:
            return self.check_downflow_path(aspath, neighbor_as, afi)

