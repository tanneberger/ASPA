
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
                elif as1 == segment.value:
                    continue
                else:
                    pair_check = self.verify_pair(as1, segment.value, afi)
                    if pair_check == Invalid:
                        return Invalid
                    elif pair_check == Unknown and semi_state == Valid:
                        semi_state = pair_check
                    as1 = segment.value
        return semi_state

    def check_downflow_path(self, aspath, neighbor_as, afi, from_ix):
        if len(aspath) == 0:
            return Invalid

        if aspath[-1].type == AS_SEQUENCE and not from_ix and aspath[-1].value != neighbor_as:
            return Invalid
        else:
            semi_state = Valid

        as1 = 0
        upflow_fragment = True
        for segment in aspath:
            if segment.type != AS_SEQUENCE:
                as1 = 0
                semi_state = Unverifiable
            elif segment.type == AS_SEQUENCE:
                if not as1:
                    as1 = segment.value
                elif as1 == segment.value:
                    continue
                else:
                    if upflow_fragment:
                        pair_check = self.verify_pair(as1, segment.value, afi)
                        if pair_check == Invalid:
                            upflow_fragment = False
                        elif pair_check == Unknown and semi_state == Valid:
                            semi_state = Unknown
                    else:
                        pair_check = self.verify_pair(segment.value, as1, afi)
                        if pair_check == Invalid:
                            return Invalid
                        elif pair_check == Unknown and semi_state == Valid:
                            semi_state = pair_check
                    as1 = segment.value

        return semi_state



