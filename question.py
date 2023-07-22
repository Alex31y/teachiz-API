class Question:
    def __init__(self):
        self._qw_id = None
        self._query = None
        self._question = None
        self._wrong_answ = None
        self._corct_answ = None
        self._upvotes = None
        self._downvotes = None

    # Getters
    def get_qw_id(self):
        return self._qw_id

    def get_query(self):
        return self._query

    def get_question(self):
        return self._question

    def get_wrong_answ(self):
        return self._wrong_answ

    def get_corct_answ(self):
        return self._corct_answ

    def get_upvotes(self):
        return self._upvotes

    def get_downvotes(self):
        return self._downvotes

    # Setters
    def set_qw_id(self, qw_id):
        self._qw_id = qw_id

    def set_query(self, query):
        self._query = query

    def set_question(self, question):
        self._question = question

    def set_wrong_answ(self, wrong_answ):
        self._wrong_answ = wrong_answ

    def set_corct_answ(self, corct_answ):
        self._corct_answ = corct_answ

    def set_upvotes(self, upvotes):
        self._upvotes = upvotes

    def set_downvotes(self, downvotes):
        self._downvotes = downvotes

    def printa(self):
        print("Non-null variables:")
        if self._qw_id is not None:
            print(f"_qw_id: {self._qw_id}")
        if self._query is not None:
            print(f"_query: {self._query}")
        if self._question is not None:
            print(f"_question: {self._question}")
        if self._wrong_answ is not None:
            print(f"_wrong_answ: {self._wrong_answ}")
        if self._corct_answ is not None:
            print(f"_corct_answ: {self._corct_answ}")
        if self._upvotes is not None:
            print(f"_upvotes: {self._upvotes}")
        if self._downvotes is not None:
            print(f"_downvotes: {self._downvotes}")
