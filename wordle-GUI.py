import numpy as np
import time
import random
from termcolor import colored

 #count the number of repetitions of each letter in a word
def letter_frequency(word):
    letter_dictionary = {}
    for letter in "abcdefghijklmnopqrstuvwxyz":
        letter_dictionary.update({letter:0})
    for letter in word:
        letter_dictionary.update({letter:(letter_dictionary[letter] + 1)})
    return letter_dictionary
    

#color each letter
def convert_to_color(guessed):
    result = []
    for item in guessed: #l-YELLOW
        letter = item.split("-")[0] #l
        color = item.split("-")[1] #YELLOW
        if color == 'GREEN ':
            result += colored(letter, 'green')
        elif color == 'YELLOW ':
            result += colored(letter, 'yellow')
        else: result += letter
    return result
            
#check each letter in a wrong attempt
def check_guess(attempt, solution): 
    letter_dictionary = letter_frequency(solution)

    guessed = []

    for i, letter in enumerate(attempt):
        if solution[i] == attempt[i]:
            letter_dictionary.update({attempt[i]:(letter_dictionary[attempt[i]] - 1)})
            j = 0
            for l in guessed: #remove previous yellow letters for repetition
                if l == letter +"-YELLOW " and letter_dictionary[letter] < 0:
                    guessed[j] = letter + "-GREY "
                j+=1

            guessed.append(letter + "-GREEN ")
            
        elif letter in solution:
            letter_dictionary.update({attempt[i]:(letter_dictionary[attempt[i]] - 1)})
            if letter_dictionary[attempt[i]] >= 0:
                guessed.append(letter + "-YELLOW ")
            else:
                guessed.append(letter + "-GREY ")
        else:
            guessed.append(letter + "-GREY ")
    #print(guessed)
    return ''.join(convert_to_color(guessed))

def grey_letter_filter(letter, possible_solutions): #letter not present in solution
    returnList = []
    for word in possible_solutions:
        if letter not in word:
            returnList.append(word)
    return returnList   

def yellow_letter_filter(letter, position, possible_solutions): #letter present in solution but not in the given position
    returnList = []
    for word in possible_solutions:
        if letter != word[position] and letter in word:
            returnList.append(word)
    return returnList

def green_letter_filter(letter, position, possible_solutions): #letter present in solution in the given position
    returnList = []
    for word in possible_solutions:
        if letter == word[position]:
            returnList.append(word)
    return returnList


#game played by the user
def user_game(): 
    print("Hi! Lets play Wordle!")
    f1 = open(r"C:\Users\gemel\Desktop\Artificial Intelligence\wordle\wordle-ai\python\words.txt", "r")
    f2 = open(r"C:\Users\gemel\Desktop\Artificial Intelligence\wordle\wordle-ai\python\wordsAllowed.txt", "r")
    possible_solutions= [i[:-1] for i in f1.readlines()] #possible Answers, changed during runtime
    allowed_words =  [i[:-1] for i in f2.readlines()]#possible entries (different from possible answers but useful to filter the data)

    solution = random.choice(possible_solutions) #Wordle secret answer
    #solution = "crepe"
    #print(solution)
    ALLOWED_GUESSES = 6
    previous_guesses = []

    for n in range (1, ALLOWED_GUESSES+1) : #cycle of guesses
        while True:
            print("\nAttempt n.",n," (", ALLOWED_GUESSES+1-n," remaining )")
            attempt = input("Please write a new 5-letter word and see the outcome: ").lower()
            if len(attempt) != 5:
                print(colored(attempt + " has not 5 letters. INVALID INPUT.", 'red'))
            elif not attempt in allowed_words:
                print(colored(attempt + " is not an allowed word. INVALID INPUT.", 'red'))
            elif attempt in previous_guesses:
                print(colored(attempt + " has already been used. INVALID INPUT.", 'red'))
            else: 
                previous_guesses.append(attempt)
                break

        #allowed attempt
        print("Your attempt is: "+attempt)
        if attempt == solution: #right guess
            print(colored(attempt, 'green'))
            print("Congratulations! You guessed the right word in just ",n," attempts!")
            exit()
        else : #wrong guess
            print(check_guess(attempt, solution))

    print("I'm sorry you lost! The correct word was: "+ solution)

# given the result of a guess, filter and return the remaing  possible solutions
def return_possible_solutions_AI(attempt, solution, possible_solutions):
    #print("Filtering possibile solutions...")

    for i, letter in enumerate(attempt):
        if solution[i] == attempt[i]:
           possible_solutions = green_letter_filter(attempt[i], i, possible_solutions)
            
        elif letter in solution:
            possible_solutions = yellow_letter_filter(attempt[i], i, possible_solutions)
        else:
            possible_solutions = grey_letter_filter(attempt[i], possible_solutions)
    #print(possible_solutions)
    return possible_solutions

#return all letters present in the possible solutions list
def letter_frequency_total(possible_solutions): 
    letter_dictionary = {}
    for letter in "abcdefghijklmnopqrstuvwxyz":
        letter_dictionary.update({letter:0})
    for word in possible_solutions:
        for letter in word:
            letter_dictionary.update({letter:(letter_dictionary[letter] + 1)})
        
    return letter_dictionary
    
#get the entropy value of all possible guesses (the lower the better)
def get_entropy(possible_solutions, allowed_words):
    word_dictionary = {}
    i=0  
    for word in allowed_words:
        word_dictionary.update({word:0})
    for word in allowed_words:
        i+=1
        temp_solutions_len_array = np.array([])
        for solution in possible_solutions:
            temp_solutions_len_array = np.append(temp_solutions_len_array, 
                len(return_possible_solutions_AI(word, solution, possible_solutions)))
            
        word_dictionary.update({word:np.mean(temp_solutions_len_array, dtype=np.float64)})
        #print("entropy done for: ",word, "at position: ",i, " / ",len(allowed_words)," [ ",len(possible_solutions)," ]")
       
    return word_dictionary


# trying to determine the best guess using a entropy-based system for every word
# entropy = the average remaining solutions if we use a specific guess (lesser remaining solutions = better guess)
# efficient but extremely time-consuming heuristic (more than 10 minutes per game)
def best_guess_entropy(n, previous_guesses, possible_solutions, allowed_words):
    print("Trying to get the best guess for attempt n.", n)
    if n == 1:
        return "slane" #best first word guess overall
    elif len(possible_solutions) < 5 or n == 6:
        print(possible_solutions)
        word_dictionary = get_entropy(possible_solutions, possible_solutions)
        return min(word_dictionary)
    else:
        print("Getting the entropy...")
        word_dictionary = get_entropy(possible_solutions, allowed_words)
        return min(word_dictionary) #best word
        

# trying to determine the best guess using a value-based system for every letter
def best_guess(n, previous_guesses, possible_solutions, allowed_words):
    print("Trying to get the best guess for attempt n.", n)
    if n == 1:
        return "slane" #best first word guess overall
    elif len(possible_solutions) < 8 or n > 4:
        letter_dictionary = letter_frequency_total(possible_solutions)
        #print(letter_dictionary)
        past_letters = []
        maxvalue = 0
        for word in possible_solutions:
            value = 0
            for letter in word:
                if letter not in past_letters: #value of word doesn't increase with repetition
                    value+= letter_dictionary[letter]
                    past_letters.append(letter)
            if value > maxvalue and word not in previous_guesses: 
                bestWord = word
                maxvalue = value
        #print(maxvalue)            #print to check the best value
        return bestWord
    else:
        letter_dictionary = letter_frequency_total(possible_solutions)
        #print(letter_dictionary)

        maxvalue = 0
        for word in allowed_words:
            past_letters = []
            value = 0
            for letter in word:
                if letter not in past_letters: #value of word doesn't increase with repetition
                    value+= letter_dictionary[letter]
                    past_letters.append(letter)
            if value > maxvalue and word not in previous_guesses: 
                bestWord = word
                maxvalue = value
        #print(maxvalue)            #print to check the best value
        return bestWord



def ai_game(): #game played by the AI
    print("Hello let's do AI game")
    start_time = time.time()
    f1 = open(r"C:\Users\gemel\Desktop\Artificial Intelligence\wordle\wordle-ai\python\words.txt", "r")
    f2 = open(r"C:\Users\gemel\Desktop\Artificial Intelligence\wordle\wordle-ai\python\wordsAllowed.txt", "r")
    possible_solutions= [i[:-1] for i in f1.readlines()] #possible Answers, changed during runtime
    allowed_words =  [i[:-1] for i in f2.readlines()]#possible entries (different from possible answers but useful to filter the data)

    solution = random.choice(possible_solutions) #Wordle secret answer
    # solution = "stone"
    print("SOLUTION: ",solution)
    ALLOWED_GUESSES = 6
    previous_guesses = []

    
    for n in range (1, ALLOWED_GUESSES+1) : #cycle of guesses
        
        while True:
            attempt = best_guess(n, previous_guesses, possible_solutions, allowed_words)
            #attempt = best_guess_entropy(n,previous_guesses, possible_solutions, allowed_words)

            print("\nAttempt n.",n," (", ALLOWED_GUESSES+1-n," remaining )")
            print("Your guess is: ",attempt)
            if len(attempt) != 5:
                print(colored(attempt + " has not 5 letters. INVALID INPUT.", 'red'))
            elif attempt in previous_guesses:
                print(colored(attempt + " has already been used. INVALID INPUT.", 'red'))
            elif not attempt in allowed_words:
                print(colored(attempt + " is not an allowed word. INVALID INPUT.", 'red'))           
            else: 
                previous_guesses.append(attempt)
                allowed_words.remove(attempt)
                break

        #allowed attempt
        print("Your attempt is: "+attempt)
        if attempt == solution: #right guess
            print(colored(attempt, 'green'))
            print("Congratulations! You guessed the right word in just ",n," attempts! TIME: ",time.time() - start_time)
            exit()
        else : #wrong guess
            print(check_guess(attempt, solution))
            possible_solutions = return_possible_solutions_AI(attempt, solution, possible_solutions)

    
    
    print("I'm sorry you lost! The correct word was: ", solution," TIME: ",time.time() - start_time)
    

def test_all_possibile_solutions(saved_possible_solutions):
    directory = r"C:\Users\gemel\Desktop\Artificial Intelligence\wordle\wordle-ai\python\results.txt"
    f = open(directory,"w")
    f.write("\n")


    print("Hello let's test the AI game through all the possible solutions")
    f2 = open(r"C:\Users\gemel\Desktop\Artificial Intelligence\wordle\wordle-ai\python\wordsAllowed.txt", "r")
    saved_allowed_words =  [i[:-1] for i in f2.readlines()]#possible entries (different from possible answers but useful to filter the data)
    total_guesses = 0
    total_start_time = time.time()
    count = 0
    for solution in saved_possible_solutions:
        start_time = time.time()
        
        previous_guesses = []
        possible_solutions = saved_possible_solutions.copy()
        allowed_words = saved_allowed_words.copy()
        count += 1
        print("n. ",count," SOLUTION: ",solution)
        ALLOWED_GUESSES = 6  

        for n in range (1, ALLOWED_GUESSES+1) : #cycle of guesses
            
            while True:
                attempt = best_guess(n, previous_guesses, possible_solutions, allowed_words)
                #attempt = best_guess_entropy(n,previous_guesses, possible_solutions, allowed_words)

                print("\nAttempt n.",n," (", ALLOWED_GUESSES+1-n," remaining )")
                print("Your guess is: ",attempt)
                if len(attempt) != 5:
                    print(colored(attempt + " has not 5 letters. INVALID INPUT.", 'red'))
                elif attempt in previous_guesses:
                    print(colored(attempt + " has already been used. INVALID INPUT.", 'red'))
                elif not attempt in allowed_words and not attempt in possible_solutions:
                    print(colored(attempt + " is not an allowed word. INVALID INPUT.", 'red'))           
                else: 
                    previous_guesses.append(attempt)
                    if attempt in allowed_words:
                        allowed_words.remove(attempt)
                    break

            #allowed attempt
            print("Your attempt is: "+attempt)
            if attempt == solution: #right guess
                success_time = round(time.time() - start_time, 4)
                total_guesses += n
                with open(directory, "a") as f:
                    f.write(str(count))
                    f.write(">")
                    f.write(solution)
                    f.write(": n_attempt ")
                    f.write(str(n))
                    f.write(" time: ")
                    f.write(str(success_time))
                    f.write('\n')
                
                break
            else : #wrong guess
                #print(check_guess(attempt, solution))
                possible_solutions = return_possible_solutions_AI(attempt, solution, possible_solutions)
    
    print("Test concluded! check results.txt for the performance!")
    f = open(directory,"a")
    total_time = round(time.time() - total_start_time, 4)
    average_time = round(total_time / (count-1), 4)
    average_guesses = round(total_guesses / (count-1), 4)
    f.write("\n Average time to find the solution: ")
    f.write(str(average_time))
    f.write("\n Average guesses: ")
    f.write(str(average_guesses))




    
    
    print("I'm sorry you lost! The correct word was: ", solution)
    with open(directory, "a") as f:
                    f.write(str(count))
                    f.write(">")
                    f.write(solution)
                    f.write(" !!! ERROR !!! ")
                    f.write('\n')



#main to launch user mode, AI mode or test mode
def main():
    f1 = open(r"C:\Users\gemel\Desktop\Artificial Intelligence\wordle\wordle-ai\python\words.txt", "r")
    possible_solutions= [i[:-1] for i in f1.readlines()]

    while True:
        mode = input("If you want to play type 'User' otherwise type 'AI' : " ).lower()
        if mode == "user":
            user_game() #let's a user play from the console panel
            break
        elif mode == "ai":
            ai_game() #starts an AI game where the guesses are printed
            break
        elif mode == "test": #starts an AI game for every possibile solution, printing ina txt file the performance
            test_all_possibile_solutions(possible_solutions)
        else:
            print(mode," is not a valid option. Please retry.")


if __name__ == "__main__":
    main()




