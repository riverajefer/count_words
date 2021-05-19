import pdftotext
 
# Load your PDF
with open("prueba.pdf", "rb") as f:
    pdf = pdftotext.PDF(f)

fileVariable = open('output.txt', 'r+')
fileVariable.truncate(0)
fileVariable.close()

# Save all text to a txt file.
with open('output.txt', 'w') as f:
    f.write("\n\n".join(pdf))



file = open("output.txt", "rt")
data = file.read()
words = data.split()

numbers = sum(c.isdigit() for c in data)
letters = sum(c.isalpha() for c in data)
spaces  = sum(c.isspace() for c in data)
others  = len(data) - numbers - letters - spaces

print('TOTAL PALABRAS :', len(words))
print('TOTAL NUMEROS :', numbers)