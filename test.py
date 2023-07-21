import wikipedia
import re

def clean_text(input_text):
    text = ""

    for char in input_text:
        try:
            char.encode('utf-8')
            text += char
        except UnicodeEncodeError:
            pass

    text = text.replace('\n', ' ')
    text = re.sub('\s+', ' ', text)
    return text

wikipedia.set_lang("it")
pagina = wikipedia.page("transformers")
#gino = wikipedia.suggest("google")
gino = clean_text(pagina.content)
print(gino)