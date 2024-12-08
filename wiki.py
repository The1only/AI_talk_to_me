import wikipedia
import wikipediaapi
#from wikipedia import wikiapi

def get_wikipedia_answer(question):
  # Extract the answer from the API response
  answer = wikipedia.summary(question, sentences = 3)
  return answer

question = "Who is Albert Einstein?"
answer = get_wikipedia_answer(question)
print(answer)