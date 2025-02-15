# Binary Analysis Next Generation (BANG!)
#
# This file is part of BANG.
#
# BANG is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License, version 3,
# as published by the Free Software Foundation.
#
# BANG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License, version 3, along with BANG.  If not, see
# <http://www.gnu.org/licenses/>
#
# Copyright Armijn Hemel
# Licensed under the terms of the GNU Affero General Public License
# version 3
# SPDX-License-Identifier: AGPL-3.0-only

import os
from UnpackParser import UnpackParser, check_condition
from UnpackParserException import UnpackParserException
from kaitaistruct import ValidationNotEqualError
from . import dtb

class DeviceTreeUnpackParser(UnpackParser):
    extensions = []
    signatures = [
        (0, b'\xd0\x0d\xfe\xed')
    ]
    pretty_name = 'dtb'

    def parse(self):
        file_size = self.fileresult.filesize
        try:
            self.data = dtb.Dtb.from_io(self.infile)
        except (Exception, ValidationNotEqualError) as e:
            raise UnpackParserException(e.args)
        check_condition(file_size >= self.data.total_size, "not enough data")
        if self.data.version > 16:
            check_condition(self.data.last_compatible_version, "invalid compatible version")
        # check some offsets
        check_condition(self.data.structure_block_offset + self.data.structure_block_size <= self.data.total_size,
                        "invalid offset/size for structure block")
        check_condition(self.data.strings_block_offset + self.data.strings_block_size <= self.data.total_size,
                        "invalid offset/size for strings block")

    # TODO: there might be systems that have kernels embedded in DTB
    # structures as described here:
    # https://elinux.org/images/f/f4/Elc2013_Fernandes.pdf

    def calculate_unpacked_size(self):
        self.unpacked_size = self.data.total_size

    def set_metadata_and_labels(self):
        """sets metadata and labels for the unpackresults"""
        labels = ['dtb', 'flattened device tree']
        metadata = {}

        self.unpack_results.set_labels(labels)
        self.unpack_results.set_metadata(metadata)
