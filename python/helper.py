from ns import Document

class DocumentHelper(Document):
    def command(self, key, path, command, *args):
        node = self.root.get_path(path)
        
