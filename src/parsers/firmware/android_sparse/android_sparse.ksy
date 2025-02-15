meta:
  id: android_sparse
  title: Android Sparse image
  file-extension: img
  tags:
    - archive
    - android
  license: CC0-1.0
  endian: le
doc: |
    The Android sparse format is a format to more efficiently store files
    for for example firmware updates to save on bandwidth. Files in sparse
    format first have to be converted back to their original format.

    A tool to create images for testing can be found in the Android source code tree:

    <https://android.googlesource.com/platform/system/core/+/7b444f0/libsparse> - `img2simg.c`

    Note: this is not the same as the Android sparse data image format.
doc-ref: https://android.googlesource.com/platform/system/core/+/7b444f0/libsparse/sparse_format.h
seq:
  - id: img_header
    type: header
  - id: img_header_entries
    type: image_header_entry
    repeat: expr
    repeat-expr: img_header.total_chunks
types:
  header:
     seq:
       - id: magic
         contents: [0x3a, 0xff, 0x26, 0xed]
       - id: version
         type: version
       - id: file_header_size
         -orig-id: file_hdr_sz
         type: u2
         doc: size of file header, should be 28
       - id: chunk_header_size
         -orig-id: chunk_hdr_sz
         type: u2
         doc: size of chunk header, should be 12
       - id: block_size
         -orig-id: blk_sz
         type: u4
         doc: block size in bytes, multiple of 4
       - id: total_blocks
         -orig-id: total_blks
         type: u4
         doc: blocks in the original data
       - id: total_chunks
         -orig-id: total_chunks
         type: u4
       - id: checksum
         -orig-id: image_checksum
         type: u4
         doc: CRC32 checksum of the original data
  image_header_entry:
    seq:
      - id: header
        type: fixed_header
      - id: body
        size: header.total_size - header._sizeof
    types:
      fixed_header:
        seq:
          - id: chunk_type
            type: u2
            enum: chunk_types
            doc: chunk type
          - id: reserved
            type: u2
          - id: chunk_size
            type: u4
            doc: in blocks in output image
          - id: total_size
            type: u4
            doc: in bytes of chunk input file including chunk header and data
  version:
    seq:
      - id: major
        -orig-id: major_version
        type: u2
        valid: 1
      - id: minor
        -orig-id: minor_version
        type: u2
enums:
  chunk_types:
    0xcac1: raw
    0xcac2: fill
    0xcac3: dont_care
    0xcac4: crc32
