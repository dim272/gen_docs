from tkinter import Tk, Label, Button

root = Tk()  # создаем корневой объект - окно
root.title("Автоматизированный Генератор Документов")  # устанавливаем заголовок окна
root.geometry("500x250")  # устанавливаем размеры окна

label = Label(text="docx templates")  # создаем текстовую метку
label.pack()  # размещаем метку в окне

clicks = 0


def click_button():
    global clicks
    clicks += 1
    # изменяем текст на кнопке
    btn["text"] = f"Clicks {clicks}"


btn = Button(text="Click", command=click_button)  # создаем кнопку из пакета ttk
btn.pack()  # размещаем кнопку в окне

root.mainloop()
