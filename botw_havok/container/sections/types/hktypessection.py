from ....binary import BinaryReader, BinaryWriter
from ....binary.types import String, UInt32
from ..base import HKSection

if False:
    from ....hkfile import HKFile


class HKTypesSection(HKSection):
    """Havok __types__ section, seems unused
    """

    id: int = 1
    tag: String = String("__types__")

    def read(self, hkFile: "HKFile", br: BinaryReader):
        super().read(hkFile, br)

    def write(self, hkFile: "HKFile", bw: BinaryWriter):
        self.absolute_offset = bw.tell()
        self.local_fixups_offset = bw.tell() - self.absolute_offset
        self.global_fixups_offset = self.local_fixups_offset
        self.virtual_fixups_offset = self.global_fixups_offset
        self.exports_offset = self.virtual_fixups_offset
        self.imports_offset = self.exports_offset
        self.EOF_offset = self.imports_offset

        bw.fill_uint32(f"{self.tag}abs", self.absolute_offset)
        bw.fill_uint32(f"{self.tag}loc", self.local_fixups_offset)
        bw.fill_uint32(f"{self.tag}glob", self.global_fixups_offset)
        bw.fill_uint32(f"{self.tag}virt", self.virtual_fixups_offset)
        bw.fill_uint32(f"{self.tag}exp", self.exports_offset)
        bw.fill_uint32(f"{self.tag}imp", self.imports_offset)
        bw.fill_uint32(f"{self.tag}eof", self.EOF_offset)