from typing import List

from ..binary import BinaryReader, BinaryWriter
from ..container.sections.util import LocalFixup
from .base import HKBase
from .common.hkRootLevelContainerNamedVariant import hkRootLevelContainerNamedVariant

if False:
    from ..hk import HK
    from ..container.sections.hkobject import HKObject


class hkRootLevelContainer(HKBase):
    namedVariants: List[hkRootLevelContainerNamedVariant]

    def __init__(self):
        super().__init__()

        self.namedVariants = []

    def deserialize(self, hk: "HK", obj: "HKObject"):
        super().deserialize(hk, obj)

        br = BinaryReader(self.hkobj.bytes)
        br.big_endian = hk.header.endian == 0

        # namedVariantsCount_offset = br.tell()
        namedVariantsCount = hk._read_counter(br)
        br.align_to(16)

        # namedVariants_offset = br.tell()
        for _ in range(namedVariantsCount):
            nv = hkRootLevelContainerNamedVariant()
            self.namedVariants.append(nv)
            nv.deserialize(hk, br, self.hkobj)

    def serialize(self, hk: "HK"):
        bw = BinaryWriter()
        bw.big_endian = hk.header.endian == 0

        namedVariantsCounter_offset = bw.tell()
        self.write_counter(hk, bw, len(self.namedVariants))
        bw.align_to(16)

        namedVariants_offset = bw.tell()
        for nv in self.namedVariants:
            nv.serialize(hk, bw)

        self.hkobj.local_fixups = [
            LocalFixup(namedVariantsCounter_offset, namedVariants_offset)
        ]

        super().serialize(hk, bw)

    def asdict(self):
        d = super().asdict()
        d.update({"namedVariants": [nv.asdict() for nv in self.namedVariants]})
        return d

    @classmethod
    def fromdict(cls, d: dict):
        inst = cls()
        inst.hkClass = d["hkClass"]
        inst.namedVariants = [
            hkRootLevelContainerNamedVariant.fromdict(nv) for nv in d["namedVariants"]
        ]

    def __repr__(self):
        return f"{self.__class__.__name__}({self.namedVariants})"
