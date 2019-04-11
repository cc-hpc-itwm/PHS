import os
import sys
from pathlib import Path
import filecmp
import tempfile
import phs.utils
from tests import def_quick_start
from tests import def_data_types_and_order
from tests import def_parameter_definition
from tests import def_post_pro_demo


def template_test_wrapper(func, relative_fixture_path):
    with tempfile.TemporaryDirectory(
            dir=os.path.dirname(__file__) + '/tmp', suffix=sys._getframe().f_code.co_name) as tmpdir:
        print(tmpdir)
        tmpdir_ex = tmpdir + '/exper'

        func(
            experiment_dir=tmpdir_ex,
            target_module_root_dir=str(Path(os.path.dirname(__file__)).parent) + '/examples/func_def')

        '''with open(tmpdir_ex + "/results/result_frame.csv") as f:
            data = f.read()
            print(data)

        with open(str(Path(os.path.dirname(__file__))) + relative_fixture_path +
                  "/results/result_frame.csv") as f:
            data = f.read()
            print(data)'''

        dcmp = filecmp.dircmp(
            os.path.dirname(__file__) + relative_fixture_path,
            tmpdir_ex,
            ignore=['additional_information_frame.csv', 'result_frame.csv', '__pycache__',
                    'worker_timeline_post.png', 'worker_timeline_post.pdf',
                    'evo_post.pdf', 'evo_post.png',
                    'parameter_combination_post.pdf', 'parameter_combination_post.png',
                    'plot_xyr_post.gif', 'plot_xyr_post_contour.gif'])

        # cmp.report_full_closure()
        print(phs.utils.comp_files_and_dirs(dcmp))
        # compared directories should be identical what means empty cmp.diff_files
        assert not phs.utils.comp_files_and_dirs(dcmp)


def test_quick_start():
    template_test_wrapper(func=def_quick_start.def_quick_start,
                          relative_fixture_path='/fixtures/fix_quick_start')


def test_data_types_and_order():
    template_test_wrapper(func=def_data_types_and_order.def_data_types_and_order,
                          relative_fixture_path='/fixtures/fix_data_types_and_order')


def test_parameter_definition():
    template_test_wrapper(func=def_parameter_definition.def_parameter_definition,
                          relative_fixture_path='/fixtures/fix_parameter_definition')


def test_post_pro_demo():
    template_test_wrapper(func=def_post_pro_demo.def_post_pro_demo,
                          relative_fixture_path='/fixtures/fix_post_pro_demo')
