class Note:
    def __init__(self):
        self._note_id = None
        self._query = ""
        self._text = ""
        self._related_query = ""
        self._pop = 0
        self._lang = ""

    # Getters
    def get_note_id(self):
        return self._note_id

    def get_query(self):
        return self._query

    def get_text(self):
        return self._text

    def get_related_query(self):
        return self._related_query

    def get_pop(self):
        return self._pop

    def get_lang(self):
        return self._lang

    # Setters
    def set_note_id(self, note_id):
        self._note_id = note_id

    def set_query(self, query):
        self._query = query

    def set_text(self, text):
        self._text = text

    def set_related_query(self, related_query):
        self._related_query = related_query

    def set_pop(self, pop):
        self._pop = pop

    def set_lang(self, lang):
        self._lang = lang

    # Method to print content
    def print_content(self):
        print("Note ID:", self._note_id)
        print("Query:", self._query)
        print("Text:", self._text)
        print("Related Query:", self._related_query)
        print("Popularity:", self._pop)
        print("Lang:", self._lang)
