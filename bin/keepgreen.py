# test github copilot

# พิมพ์ตรงนี้
# function to encrypt text with a random key
# โผล่ตรงนั้น ------------------------------------------>

def encrypt(text, key):
    encrypted_text = ""
    # loop through all characters in plain text
    for i in range(len(text)):
        # get ASCII value of character
        char = ord(text[i])
        # add key to the ASCII value
        char += key
        # convert ASCII value back to character and add to encrypted text
        encrypted_text += chr(char)
    return encrypted_text

def encrypt2(text, key):
    # create a list of the alphabet
    alphabet = []
    for letter in range(97, 123):
        alphabet.append(chr(letter))
    # create a list to store the encrypted text
    encrypted_text = []
    # loop through the text
    for letter in text:
        # find the index of the letter in the alphabet
        index = alphabet.index(letter)
        # add the key to the index
        index += key
        # if the index is greater than the length of the alphabet
        if index > len(alphabet) - 1:
            # subtract the length of the alphabet from the index
            index -= len(alphabet)
        # add the letter at the index to the encrypted text
        encrypted_text.append(alphabet[index])
    # join the encrypted text and return it
    return "".join(encrypted_text)