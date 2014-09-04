""" Test the utility functions in the dodo file.
"""
import os, shutil, tempfile

from nose import with_setup

from uristmaps import uristcopy

class TestUristmaps:

    # Files and directories to use in tests
    test_dir_a = None
    file_a_1 = None
    file_a_2 = None

    test_dir_b = None
    file_b_1 = None
    file_b_2 = None

    def setup(self):
        self.test_dir_a = tempfile.mkdtemp()
        self.file_a_1 = os.path.join(self.test_dir_a, "file_1.txt")
    
        self.test_dir_b = tempfile.mkdtemp()


    def teardown(self):
        """ Delete the temporary directories.
        """
        shutil.rmtree(self.test_dir_a)
        shutil.rmtree(self.test_dir_b)

    def test_copy(self):
        """ Test the standard file copy function.
        """
        with open(self.file_a_1, "w") as file_a:
            file_a.write("This is demo text.")
        
        # Assert that there is no file_1.txt yet in test_dir_b
        assert not os.path.exists(os.path.join(self.test_dir_b, "file_1.txt")), "File already exists in test_dir_b!"

        uristcopy.copy_dir_contents(self.test_dir_a, self.test_dir_b)

        # Assert that there is a file_1.txt in test_dir_b now
        assert os.path.exists(os.path.join(self.test_dir_b, "file_1.txt")), "file_1.txt has not been successfully copied into test_dir_b!"

        # Assert that there is no subdirectory named after test_dir_a in test_dir_b
        assert not os.path.exists(os.path.join(self.test_dir_b, os.path.basename(self.test_dir_a))), "test_dir_a has been copied into test_dir_b!"
    


    
