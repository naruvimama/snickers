
# Watchdog code borrowed from : http://brunorocha.org/python/watching-a-directory-for-file-changes-with-python.html
import time, yaml, os, unittest, re
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler, RegexMatchingEventHandler

re_test_module = re.compile(r'^test_.*.py$')

def read_config():
    pass

def run_tests(pattern=None):
    test_loader = unittest.TestLoader()
    print("Now testing pattern : {}".format(pattern))
    if pattern is None:
        pattern = 'test*.py'
    discovered_tests = test_loader.discover('./', pattern)
    print(discovered_tests)
    test_result = unittest.TestResult()

    discovered_tests.run(test_result)
    print(test_result)

def un_camelise(file_name):
    return ''.join(['_{}'.format(u.lower()) if u.isupper() else u for u in file_name])

def get_test_pattern(src_path):
    file_name = os.path.basename(src_path)
    if re_test_module.match(file_name):
        return file_name.split('.')[0]
    return 'test_' + un_camelise(file_name)

class ChangeHandler(PatternMatchingEventHandler):
    patterns = ["*.py"] #, "*.xml", "*.csv", "*.tsv", "*.txt"

    def process(self, event):
        """
        event.event_type
            'modified' | 'created' | 'moved' | 'deleted'
        event.is_directory
            True | False
        event.src_path
            path/to/observed/file
        """
        # the file will be processed there
        print(event.src_path, event.event_type)  # print now only for degug
        test_pattern = get_test_pattern(event.src_path)
        run_tests(test_pattern)

    def on_modified(self, event):
        self.process(event)

if __name__ == '__main__':
    config = read_config()
    observer = Observer()
    observer.schedule(ChangeHandler(), path=os.getcwd(), recursive=True)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
