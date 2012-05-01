from ns import Document

class DocumentHelper(Document):
    def command(self, path, command, *args):
        if command in ('incr', 'decr',):
            pass
        
            
