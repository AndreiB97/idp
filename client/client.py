from tkinter import messagebox
from tkinter import *
import os
import requests

window = None

top_frame = None
bottom_frame = None

vote_text = None

red_button = None
blue_button = None

next_button = None
prev_button = None

like_button = None
dislike_button = None

submit_button = None

answer_text_1 = None
answer_text_2 = None
answer_entry_1 = None
answer_entry_2 = None

answer_frame_top = None
answer_frame_bottom = None

send_button = None
send_frame = None

back_button = None

check_mark_label = None

NOT_VOTED = 0
VOTED_RED = 1
VOTED_BLUE = 2

QUESTION_LIKED = 1
QUESTION_DISLIKED = 2

questions = []
current_question = 0

SERVER_URL = os.environ.get('SERVER_URL') or 'localhost'


def init_ui_widgets():
    global window, top_frame, vote_text, bottom_frame, red_button, blue_button, next_button, \
        prev_button, submit_button, answer_text_1, answer_text_2, answer_entry_1, answer_entry_2, \
        answer_frame_top, answer_frame_bottom, send_button, send_frame, check_mark_label, \
        like_button, dislike_button, back_button

    # className requires a space or the first letter of the string is not capitalized
    window = Tk(className=' Would You Rather')
    window.resizable(False, False)

    top_frame = Frame(window)
    bottom_frame = Frame(window)

    vote_text = Label(top_frame, text='Would you rather...', font=('calibri', 20))

    red_button = Button(bottom_frame, text='Left', bg='red', fg='white',
                        command=pick_red, height=5, width=32, font=('calibri', 20), wraplength=400)
    blue_button = Button(bottom_frame, text='Right', bg='blue', fg='white',
                         command=pick_blue, height=5, width=32, font=('calibri', 20), wraplength=400)

    next_button = Button(bottom_frame, text='>', bg='#555555', fg='white',
                         command=get_next, height=1, width=1, font=('calibri', 12))
    prev_button = Button(bottom_frame, text='<', bg='#555555', fg='white',
                         command=get_prev, height=1, width=1, font=('calibri', 12), state=DISABLED)

    like_button = Button(bottom_frame, text='👍', bg='#555555', fg='white',
                         command=like_question, height=1, width=1, font=('calibri', 12))
    dislike_button = Button(bottom_frame, text='👎', bg='#555555', fg='white',
                            command=dislike_question, height=1, width=1, font=('calibri', 12))

    submit_button = Button(bottom_frame, text='Submit question',
                           command=display_submit_ui, font=('calibri', 11))

    answer_frame_top = Frame(window)
    answer_frame_bottom = Frame(window)

    answer_text_1 = Label(answer_frame_top, text="Red", font=('calibri', 15))
    answer_entry_1 = Entry(answer_frame_top, font=('calibri', 15))

    answer_text_2 = Label(answer_frame_bottom, text="Blue", font=('calibri', 15))
    answer_entry_2 = Entry(answer_frame_bottom, font=('calibri', 15))

    send_frame = Frame(window)

    send_button = Button(send_frame, text='Send', command=send_question, font=('calibri', 11))
    back_button = Button(send_frame, text='Back', command=display_vote_ui, font=('calibri', 11))

    check_mark_label = Label(bottom_frame, text='✓', fg='white', font=('calibri', 15))


def display_vote_ui():
    # hide submit ui
    answer_frame_top.pack_forget()
    answer_frame_bottom.pack_forget()
    send_frame.pack_forget()

    top_frame.pack()
    vote_text.pack()

    bottom_frame.pack(side=BOTTOM)

    prev_button.grid(row=0, column=0)
    next_button.grid(row=0, column=3)

    red_button.grid(row=0, column=1)
    blue_button.grid(row=0, column=2)

    submit_button.grid(row=1, column=2, pady=5)


def display_submit_ui():
    # hide vote ui
    bottom_frame.pack_forget()

    answer_frame_top.pack()
    answer_frame_bottom.pack()
    send_frame.pack()

    answer_text_1.pack(side=LEFT)
    answer_entry_1.pack(side=RIGHT)

    answer_text_2.pack(side=LEFT)
    answer_entry_2.pack(side=RIGHT)

    send_button.pack(side=RIGHT)

    back_button.pack(side=LEFT)


def pick_red():
    if questions[current_question]['state'] == NOT_VOTED:
        red_button.configure(relief=SUNKEN)
        questions[current_question]['state'] = VOTED_RED

        para = {
            'id': questions[current_question]['id'],
            'answer': 'red'
        }

        requests.put(f'http://{SERVER_URL}/answers', params=para)
        display_result()


def pick_blue():
    if questions[current_question]['state'] == NOT_VOTED:
        blue_button.configure(relief=SUNKEN)
        questions[current_question]['state'] = VOTED_BLUE

        para = {
            'id': questions[current_question]['id'],
            'answer': 'blue'
        }

        requests.put(f'http://{SERVER_URL}/answers', params=para)
        display_result()


def get_next():
    global current_question

    current_question -=- 1

    # reset buttons
    red_button.configure(relief=RAISED)
    blue_button.configure(relief=RAISED)

    like_button.configure(relief=RAISED)
    dislike_button.configure(relief=RAISED)

    prev_button.config(state=NORMAL)

    if current_question >= len(questions):
        new_question = get_question()
        questions.append(new_question)

        check_mark_label.grid_forget()

        like_button.grid_forget()
        dislike_button.grid_forget()

        display_question()
    else:
        new_question = questions[current_question]

        if new_question['state'] == NOT_VOTED:
            check_mark_label.grid_forget()

            like_button.grid_forget()
            dislike_button.grid_forget()

            display_question()
        else:
            display_result()


def get_prev():
    global current_question

    red_button.configure(relief=RAISED)
    blue_button.configure(relief=RAISED)

    if current_question > 0:
        current_question -= 1

        # disable button if on first question
        if current_question == 0:
            prev_button.config(state=DISABLED)

    if questions[current_question]['state'] == NOT_VOTED:
        display_question()
    else:
        display_result()


def send_question():
    # strip whitespaces from answers
    ans1_text = answer_entry_1.get().strip()
    ans2_text = answer_entry_2.get().strip()

    if len(ans1_text) == 0 or len(ans2_text) == 0:
        messagebox.showinfo('Error', 'Answer cannot be blank')
    elif len(ans1_text) > 128 or len(ans2_text) > 128:
        messagebox.showinfo('Error', 'Answer length must be 128 or less characters')
    else:
        para = {
            'answer1': ans1_text,
            'answer2': ans2_text
        }

        requests.put(f'http://{SERVER_URL}/questions', params=para)

        answer_entry_1.delete(0, END)
        answer_entry_2.delete(0, END)

        display_vote_ui()


def get_question():
    req = requests.get(url=f'http://{SERVER_URL}/questions')
    question = req.json()
    question['state'] = NOT_VOTED
    question['voted'] = NOT_VOTED

    return question


def display_question():
    red_button.configure(text=questions[current_question]['red'])
    blue_button.configure(text=questions[current_question]['blue'])


def display_result():
    red_votes = questions[current_question]['red_stats']
    blue_votes = questions[current_question]['blue_stats']

    like_button.grid(row=1, column=1, padx=(0, 30))
    dislike_button.grid(row=1, column=1, padx=(30, 0))

    if questions[current_question]['state'] == VOTED_RED:
        red_votes -=- 1
        check_mark_label.configure(bg='red')
        check_mark_label.grid(row=0, column=1, padx=(0, 370), pady=(0, 140))
        red_button.configure(relief=SUNKEN)
    elif questions[current_question]['state'] == VOTED_BLUE:
        blue_votes -=- 1
        check_mark_label.configure(bg='blue')
        check_mark_label.grid(row=0, column=2, padx=(0, 370), pady=(0, 140))
        blue_button.configure(relief=SUNKEN)

    if questions[current_question]['voted'] == QUESTION_LIKED:
        like_button.configure(relief=SUNKEN)
        dislike_button.configure(relief=RAISED)
    elif questions[current_question]['voted'] == QUESTION_DISLIKED:
        dislike_button.configure(relief=SUNKEN)
        like_button.configure(relief=RAISED)

    red_percent = 100 * red_votes / (red_votes + blue_votes)
    blue_percent = 100 * blue_votes / (red_votes + blue_votes)

    red_button.configure(text=f'{red_percent:.2f}%\n'
                              f'{red_votes} votes\n'
                              f'{questions[current_question]["red"]}')
    blue_button.configure(text=f'{blue_percent:.2f}%\n'
                               f'{blue_votes} votes\n'
                               f'{questions[current_question]["blue"]}\n')


def like_question():
    if questions[current_question]['voted'] != QUESTION_LIKED:
        like_button.configure(relief=SUNKEN)
        dislike_button.configure(relief=RAISED)

        questions[current_question]['voted'] = QUESTION_LIKED

        para = {
            'id': questions[current_question]['id'],
            'score': 1
        }

        requests.put(f'http://{SERVER_URL}/score', params=para)


def dislike_question():
    if questions[current_question]['voted'] != QUESTION_DISLIKED:
        like_button.configure(relief=RAISED)
        dislike_button.configure(relief=SUNKEN)

        questions[current_question]['voted'] = QUESTION_DISLIKED

        para = {
            'id': questions[current_question]['id'],
            'score': -1
        }

        requests.put(f'http://{SERVER_URL}/score', params=para)


if __name__ == '__main__':
    init_ui_widgets()
    questions.append(get_question())
    display_question()
    display_vote_ui()
    question_state = NOT_VOTED
    window.mainloop()
