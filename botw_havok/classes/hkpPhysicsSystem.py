from typing import List

from ..binary import BinaryReader, BinaryWriter
from ..container.sections.util import GlobalReference, LocalFixup
from .base import HKBase
from .common.hkReferencedObject import hkReferencedObject
from .hkpRigidBody import hkpRigidBody

if False:
    from ..hk import HK
    from ..container.sections.hkobject import HKObject


class hkpPhysicsSystem(HKBase, hkReferencedObject):
    """Physics system, contains rigid bodies
    """

    rigidBodies: List[hkpRigidBody]
    # constraints: List[hkpConstraintInstance] TODO: CONSTRAINTS
    # actions: List[hkpAction] # Doesn't seem used
    # phantoms: List[hkpPhantom] # Doesn't seem used

    name: str
    userData: int
    active: bool

    def __init__(self):
        super().__init__()

        self.rigidBodies = []

    def deserialize(self, hk: "HK", obj: "HKObject"):
        HKBase.deserialize(self, hk, obj)

        br = BinaryReader(self.hkobj.bytes)
        br.big_endian = hk.header.endian == 0

        hkReferencedObject.deserialize(self, hk, br)
        if hk.header.padding_option:
            br.align_to(16)

        # ----

        rigidBodiesCount_offset = br.tell()
        rigidBodiesCount = hk._read_counter(br)

        constraintsCount_offset = br.tell()
        constraintsCount = hk._read_counter(br)

        actionsCount_offset = br.tell()
        actionsCount = hk._read_counter(br)

        phantomsCount_offset = br.tell()
        phantomsCount = hk._read_counter(br)

        namePointer_offset = br.tell()
        hk._assert_pointer(br)

        # ----
        # U64 on Switch, U32 on WiiU?
        if hk.header.pointer_size == 8:
            self.userData = br.read_uint64()
        elif hk.header.pointer_size == 4:
            self.userData = br.read_uint32()

        self.active = bool(br.read_int8())
        br.align_to(16)

        # ----

        for gr in obj.global_references:
            if gr.src_rel_offset == br.tell():
                hk.data.objects.remove(gr.dst_obj)

                rb = hkpRigidBody()
                self.rigidBodies.append(rb)
                rb.deserialize(hk, gr.dst_obj)

                hk._assert_pointer(br)
        br.align_to(16)

        self.name = br.read_string()
        br.align_to(16)

        obj.local_fixups.clear()
        obj.global_references.clear()

    def serialize(self, hk: "HK"):
        bw = BinaryWriter()
        bw.big_endian = hk.header.endian == 0

        hkReferencedObject.serialize(self, hk, bw)
        if hk.header.padding_option:
            bw.align_to(16)

        # ----

        rigidBodiesCount_offset = bw.tell()
        self.write_counter(hk, bw, len(self.rigidBodies))

        # Constraints counter here

        bw.align_to(16)

        # ----

        if hk.header.pointer_size == 8:
            bw.write_uint64(self.userData)
        elif hk.header.pointer_size == 4:
            bw.write_uint32(self.userData)
        else:
            raise NotImplementedError("idk really")

        bw.write_int8(int(self.active))
        bw.align_to(16)

        # ----

        for rb in self.rigidBodies:
            rb.serialize(hk, bw)
            hk.data.objects.append(rb.hkobj)

            gr = GlobalReference()
            gr.src_obj = self.hkobj
            gr.src_rel_offset = bw.tell()
            gr.dst_obj = rb.hkobj
            self.hkobj.global_references.append(gr)

            hk._write_empty_pointer(bw)
        bw.align_to(16)

        # Constraints data here

        bw.write_string(self.name)
        bw.align_to(16)

        HKBase.serialize(self, hk, bw)

    def asdict(self):
        d = super().asdict()
        d.update(hkReferencedObject.asdict(self))
        d.update(
            {
                "rigidBodies": [rb.asdict() for rb in self.rigidBodies],
                "name": self.name,
                "userData": self.userData,
                "active": self.active,
            }
        )
        return d

    @classmethod
    def fromdict(cls, d: dict):
        inst = cls()
        inst.hkClass = d["hkClass"]
        inst.memSizeAndRefCount = d["memSizeAndRefCount"]
        inst.rigidBodies = [hkpRigidBody.fromdict(rb) for rb in d["rigidBodies"]]
        inst.name = d["name"]
        inst.userData = d["userData"]
        inst.active = d["active"]

        return super().fromdict(d)

    def __repr__(self):
        return "<{}({}, {}, {}, {})>".format(
            self.__class__.__name__,
            self.name,
            self.active,
            self.rigidBodies,
            self.userData,
        )
