import inspect
import pkgutil
from operator import itemgetter

from .TestUtil import *

from Unpacker import *

import bangsignatures
import bangandroid
import bangmedia
import bangfilesystems
import bangunpack
import importlib

import parsers
from UnpackParser import UnpackParser

def get_unpackers_for_extension(ext):
    return bangsignatures.extension_to_unpackparser.get(ext, [])

def get_unpackers_for_file(unpackername, f):
    ext = pathlib.Path(f).suffix

    unpackers = { u for u in bangsignatures.get_unpackers()
            if u.is_valid_extension(ext)
            or u.pretty_name == unpackername }

    for u in unpackers: yield u
    
def is_prefix(pref, full):
    cp = os.path.commonprefix((pref, full))
    return cp == pref

class TestUnpackResult(TestBase):
    def test_unpackdata_for_all_unpackers(self):
        unpackers = set(bangsignatures.get_unpackers())
        tested_unpackers = { u for f, u
                in self.walk_available_files_with_unpackers() }
        untested_unpackers = unpackers.difference(tested_unpackers)
        print("no tests for:")
        print("\n".join([u.__name__ for u in untested_unpackers]))
        self.assertEqual(untested_unpackers, set([]))

    def walk_available_files_with_unpackers(self):
        testfilesdir = self.testdata_dir / 'unpackers'
        for dirpath, dirnames, filenames in os.walk(testfilesdir):
            unpackername = os.path.basename(dirpath)
            for f in filenames:
                relativename = pathlib.Path(dirpath).relative_to(self.testdata_dir) / f
                for unpacker in get_unpackers_for_file(unpackername, f):
                    yield str(relativename), unpacker

    def test_unpackresult_has_correct_filenames(self):
        unpacker = Unpacker(self.unpackdir)
        skipfiles = [
            'unpackers/zip/test-add-random-data.zip',
            'unpackers/zip/test-data-replaced-in-middle.zip',
            'unpackers/zip/test-prepend-random-data.zip',
            # 'unpackers/squashfs/test-add-random-data.sqsh',
            # 'unpackers/squashfs/test-cut-data-from-end-add-random.sqsh',
            # 'unpackers/squashfs/test-cut-data-from-end.sqsh',
            # 'unpackers/squashfs/test-data-replaced-in-middle.sqsh',
            ]
        for fn, unpackparser in \
            sorted(set(self.walk_available_files_with_unpackers()),
                key=itemgetter(0)):
            if fn in skipfiles:
                continue
            self._copy_file_from_testdata(fn)
            unpacker.make_data_unpack_directory(fn, unpackparser.__name__, 0)
            fileresult = create_fileresult_for_path(self.unpackdir,
                    pathlib.Path(fn), set())
            up = unpackparser(fileresult, self.scan_environment)
            unpackresult = up.parse_and_unpack(fileresult, self.scan_environment, 0, unpacker.get_data_unpack_directory())

            try:
                # all paths in unpackresults are relative to unpackdir
                for unpackedfile, unpackedlabel in unpackresult['filesandlabels']:
                    self.assertFalse(
                        is_prefix(str(self.unpackdir), unpackedfile)
                        , f"absolute path in unpackresults: {unpackedfile}")

                    self.assertTrue(
                        is_prefix(
                            unpacker.get_data_unpack_directory(),
                            unpackedfile),
                        f"unpackedfile {unpackedfile} not in dataunpackdirectory {unpacker.get_data_unpack_directory()}"
                        )

                    self.assertTrue(
                        is_prefix(
                            unpacker.get_data_unpack_directory(),
                            os.path.normpath(unpackedfile)),
                        f"unpackedfile {os.path.normpath(unpackedfile)} not in dataunpackdirectory {unpacker.get_data_unpack_directory()}"
                        )

                    unpackedfile_full = self.scan_environment.unpack_path(unpackedfile)
                    self.assertTrue(os.path.exists(unpackedfile_full), f"path {unpackedfile_full} does not exist!")

            except KeyError as e:
                pass
            finally:
                unpacker.remove_data_unpack_directory_tree()

    def todo_test_unpackers_throw_exceptions(self):
        unpackers = get_unpackers()
        # feed a zero length file
        fn = "/dev/null"
        name = "null"
        self._copy_file_from_testdata(fn, name)
        fileresult = create_fileresult_for_path(self.unpackdir,
                pathlib.Path(name), set())
        self.assertEqual(str(fileresult.filename), name)
        for unpackername in sorted(unpackers.keys()):
            unpackparser = unpackers[unpackername]
            up = unpackparser(fileresult, self.scan_environment)
            unpackresult = up.parse_and_unpack(fileresult, self.scan_environment, 0, self.unpackdir)

if __name__ == "__main__":
    unittest.main()
