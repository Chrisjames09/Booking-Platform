import os

class Video:
    _id_counter_file = 'video_id_counter.txt'

    @classmethod
    def _load_id_counter(cls):
        if os.path.exists(cls._id_counter_file):
            with open(cls._id_counter_file, 'r') as file:
                return int(file.read().strip())
        return 1  # Start from 1 if the file does not exist

    @classmethod
    def _save_id_counter(cls, counter):
        with open(cls._id_counter_file, 'w') as file:
            file.write(str(counter))

    def __init__(self, title, file_path, description=""):
        self.video_id = Video._load_id_counter()  # Load the current ID
        self.title = title
        self.file_path = file_path
        self.description = description

        Video._save_id_counter(self.video_id + 1)  # Increment ID for the next video

    def get_id(self):
        return self.video_id

    def __str__(self):
        return f"Video(ID: {self.video_id}, Title: {self.title}, Description: {self.description}, Path: {self.file_path})"