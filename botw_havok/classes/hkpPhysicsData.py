from ..binary import BinaryReader, BinaryWriter
from ..container.sections.util import GlobalReference, LocalFixup
from .base import HKBase
from .common.hkReferencedObject import hkReferencedObject
from .hkpPhysicsSystem import hkpPhysicsSystem
from typing import List

if False:
    from ..hk import HK
    from ..container.sections.data import HKObject


class hkpPhysicsData(HKBase, hkReferencedObject):
    """Physics data container, contains references
    to world info physics systems
    """

    # worldCinfo: hkpWorldCinfo  # Doesn't seem to be used in BotW (?)
    systems: List[hkpPhysicsSystem]

    def __init__(self):
        super().__init__()  # HKBase

        self.systems = []

    def deserialize(self, hk: "HK", obj: "HKObject"):
        HKBase.deserialize(self, hk, obj)

        br = BinaryReader(obj.bytes)
        br.big_endian = hk.header.endian == 0

        # Read base referenced object data
        hkReferencedObject.deserialize(self, hk, br)

        # worldCinfo_offset = br.tell()
        hk._assert_pointer(br)

        # systemCount_offset = br.tell()
        systemCount = self.read_counter(hk, br)
        br.align_to(16)

        # systems_offset = br.read()

        for gr in obj.global_references:
            if gr.src_rel_offset == br.tell():
                system = hkpPhysicsSystem()
                system.deserialize(hk, gr.dst_obj)
                hk.data.objects.remove(gr.dst_obj)
                self.systems.append(system)

                hk._assert_pointer(br)
        br.align_to(16)

        obj.global_references.clear()

    def serialize(self, hk: "HK"):
        bw = BinaryWriter()
        bw.big_endian = hk.header.endian == 0

        hkReferencedObject.serialize(hk, bw)

        # worldCinfo_offset = bw.tell()
        hk._write_empty_pointer(bw)

        systemCount_offset = bw.tell()
        self.write_counter(hk, bw, len(self.systems))
        bw.align_to(16)

        systems_offset = bw.tell()
        for system in self.systems:
            system.serialize(hk)
            hk.data.objects.append(system.hkobj)

            gr = GlobalReference()
            gr.src_obj = self.hkobj
            gr.src_rel_offset = bw.tell()
            gr.dst_obj = system.hkobj
            self.hkobj.global_references.append(gr)

            hk._write_empty_pointer(bw)
        bw.align_to(16)

        HKBase.serialize(self, hk, bw)

    def asdict(self):
        d = hkReferencedObject.asdict(self)
        d.update(
            {
                # "worldCinfo": self.worldCinfo,
                "systems": [ps.asdict() for ps in self.systems],
            }
        )

    @classmethod
    def fromdict(cls, d: dict):
        inst = cls()
        # inst.worldCinfo = d['worldCinfo']
        inst.systems = [hkpPhysicsSystem.fromdict(ps) for ps in d["systems"]]
