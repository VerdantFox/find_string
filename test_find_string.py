from __future__ import print_function
from unittest import TestCase
from find_string import find_string
from click.testing import CliRunner


class TestFindString(TestCase):
    @classmethod
    def setUpClass(self):
        self.runner = CliRunner()
        self.CRAZY_none = self.runner.invoke(find_string, args=['CRAZY', ])
        self.crazy_none = self.runner.invoke(find_string, args=['crazy', ])

    def test_no_args(self):
        """Test no extra args produce proper dictionary output under all circumstances"""
        # With CRAZY
        assert self.CRAZY_none.exit_code == 0
        assert "no_ext_python -> lines: [4, 6, 8, 9]" in self.CRAZY_none.output
        assert "python1_check.py -> lines: [2, 4, 6, 7]" in self.CRAZY_none.output
        assert "up_one_level/python_check2.py -> lines: [7]" in self.CRAZY_none.output
        assert "xquery1.xqy -> lines: [8, 15, 18]" in self.CRAZY_none.output
        assert "text_check.txt -> lines: [6]" in self.CRAZY_none.output
        assert "up_one_level/up_two_levels/python_check3.py -> lines: [3, 5]" in self.CRAZY_none.output

        # With crazy
        assert "no_ext_python -> lines: [9, 10]" in self.crazy_none.output
        assert "up_one_level/python_check2.py -> lines: [8]" in self.crazy_none.output
        assert "xquery1.xqy -> lines: [16, 17, 19]" in self.crazy_none.output
        assert "up_one_level/python_check2.py -> lines: [8]" in self.crazy_none.output
        assert "up_one_level/up_two_levels/python_check3.py -> lines: [7, 9]" in self.crazy_none.output

    def test_case_insensitive(self):
        """Test case insensitive arguments work as intended"""
        CRAZY_case1 = self.runner.invoke(find_string, args=['CRAZY', '-c', ])
        CRAZY_case2 = self.runner.invoke(find_string, args=['CRAZY', '--case-insensitive', ])
        crazy_case1 = self.runner.invoke(find_string, args=['crazy', '-c', ])
        crazy_case2 = self.runner.invoke(find_string, args=['crazy', '-c', '--case-insensitive', ])

        # Equality between case insensitive outputs
        assert (CRAZY_case1.output.lower() ==
                CRAZY_case2.output.lower() ==
                crazy_case1.output.lower())
        # CRAZY_case1 tests
        assert "no_ext_python -> lines: [4, 6, 8, 9, 10]" in CRAZY_case1.output
        assert "python1_check.py -> lines: [2, 4, 6, 7, 8, 9]" in CRAZY_case1.output
        assert "up_one_level/python_check2.py -> lines: [7, 8]" in CRAZY_case1.output
        assert "xquery1.xqy -> lines: [8, 15, 16, 17, 18, 19]" in CRAZY_case1.output

    def test_directory(self):
        """Test directory arguments work as intended"""
        crazy_dir1 = self.runner.invoke(find_string, args=['crazy', '-d', 'up_one_level', ])
        crazy_dir2 = self.runner.invoke(find_string, args=['crazy', '--directory', 'up_one_level', ])
        crazy_dir3 = self.runner.invoke(find_string, args=['crazy', '-d', 'up_one_level/fake_dir', ])
        crazy_dir4 = self.runner.invoke(find_string, args=['crazy', '-d', 'up_one_level/up_two_levels', ])
        crazy_dir5 = self.runner.invoke(find_string, args=['crazy', '-d', '/up_one_level/up_two_levels/', ])

        # equality check
        assert crazy_dir1.output == crazy_dir2.output != crazy_dir4.output
        assert crazy_dir4.output == crazy_dir5.output
        assert crazy_dir4.exit_code == crazy_dir5.exit_code

        # Test for bad directory
        assert crazy_dir3.exit_code == 2
        assert "/up_one_level/fake_dir does not exist!" in crazy_dir3.output

        # Test contents
        assert "up_one_level/python_check2.py -> lines: [8]" in crazy_dir1.output
        assert "up_one_level/up_two_levels/python_check3.py -> lines: [7, 9]" in crazy_dir1.output
        assert "up_one_level/python_check2.py -> lines: [8]" not in crazy_dir4.output
        assert "up_one_level/up_two_levels/python_check3.py -> lines: [7, 9]" in crazy_dir4.output

    def test_extension(self):
        """Test extension arguments work as intended"""
        crazy_py_ext1 = self.runner.invoke(find_string, args=['crazy', '-e', '.py'])
        crazy_py_ext2 = self.runner.invoke(find_string, args=['crazy', '--extension', '.py'])
        crazy_bad_ext = self.runner.invoke(find_string, args=['crazy', '-e', 'py'])

        # Equality check
        assert crazy_py_ext1.output == crazy_py_ext2.output != self.crazy_none

        # Test for bad extension
        assert crazy_bad_ext.exit_code == 2
        assert "Invalid value: 'py' is not a recognized file extension" in crazy_bad_ext.output
        # Test for expected and not expected content
        assert "python1_check.py -> lines: [2, 8, 9]" in crazy_py_ext1.output
        assert "up_one_level/python_check2.py -> lines: [8]" in crazy_py_ext1.output
        assert "text_check.txt -> lines: [8]" not in crazy_py_ext1.output
        assert "xquery1.xqy -> lines: [16]" not in crazy_py_ext1.output
        assert "no_ext_python -> lines: [10]" not in crazy_py_ext1.output

    def test_ignore_comments(self):
        """Test ignore comments arguments work as intended"""
        crazy_comments1 = self.runner.invoke(find_string, args=["crazy", '-i'])
        crazy_comments2 = self.runner.invoke(find_string, args=["crazy", '--ignore-comments'])
        crazy_comments_py = self.runner.invoke(find_string, args=['crazy', '-i', '-e', '.py'])
        crazy_comments_sh = self.runner.invoke(find_string, args=['crazy', '-i', '-e', '.sh'])
        crazy_comments_xqy = self.runner.invoke(find_string, args=['crazy', '-i', '-e', '.xqy'])

        # Equality check
        assert crazy_comments1.output == crazy_comments2.output != crazy_comments_py.output

        # Test for expected and not expected content
        # All file types
        assert "bash_check.sh -> lines: [4]" in crazy_comments1.output
        assert "no_ext_bash -> lines: [4]" in crazy_comments1.output
        assert "no_ext_python -> lines: [10]" in crazy_comments1.output
        assert "python1_check.py -> lines: [8]" in crazy_comments1.output
        assert "text_check.txt -> lines: [8]" in crazy_comments1.output
        assert "xquery1.xqy -> lines: [16, 19]" in crazy_comments1.output
        # .py extension specified
        assert "python1_check.py -> lines: [8]" in crazy_comments_py.output
        assert "no_ext_python -> lines: [10]" not in crazy_comments_py.output
        # .sh extension specified
        assert "bash_check.sh -> lines: [4]" in crazy_comments_sh.output
        assert "no_ext_bash -> lines: [4]" not in crazy_comments_sh.output
        # .xqy extension specified
        assert "xquery1.xqy -> lines: [16, 19]" in crazy_comments_xqy.output

    def test_entry_methods(self):
        """Test click entry and paramater methods work as intended"""
        entry1 = self.runner.invoke(find_string, args=['crazy', '-i', '-c', '-e', '.py', '-d', 'up_one_level'])
        entry2 = self.runner.invoke(find_string, args=['crazy', '-ic', '-e', '.py', '-d', 'up_one_level'])
        entry3 = self.runner.invoke(find_string, args=['-ic', '-e', '.py', '-d', 'up_one_level', 'crazy'])
        entry_error1 = self.runner.invoke(find_string, args=['crazy', '-a'])
        entry_error2 = self.runner.invoke(find_string, args=['crazy', '-e'])
        entry_error3 = self.runner.invoke(find_string, args=['crazy', '-d'])
        entry_error4 = self.runner.invoke(find_string, args=['crazy', '-i', 'extra_param'])
        entry_error5 = self.runner.invoke(find_string, args=['crazy', 'extra_param'])
        entry_error6 = self.runner.invoke(find_string, args=['-i'])
        entry_error7 = self.runner.invoke(find_string, args=['-a'])

        # All settings work with all expected different param arrangements
        assert entry1.exit_code == entry2.exit_code == entry3.exit_code == 0
        assert entry1.output == entry2.output == entry3.output

        # Incorrect setups don't work
        assert (entry_error1.exit_code == entry_error2.exit_code ==
                entry_error3.exit_code == entry_error4.exit_code ==
                entry_error5.exit_code == entry_error6.exit_code ==
                entry_error7.exit_code == 2)





