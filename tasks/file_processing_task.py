from pathlib import Path
from tasks.base_task import BaseTask
class FileProcessingTask(BaseTask):
    def execute(self):
        path = Path(self.file_path)
        if not path.exists():
            self.logger.warning("File not found: %s", path)
            return
        if path.is_dir():
            file_count = 0
            for item in path.iterdir():
                if item.is_file():
                    file_count += 1
            self.logger.info("Folder has %s file(s): %s", file_count, path)
            return

        text = path.read_text(encoding="utf-8")
        line_count = len(text.splitlines())
        word_count = len(text.split())
        self.logger.info("File: %s", path)
        self.logger.info("Lines: %s", line_count)
        self.logger.info("Words: %s", word_count)
