from tkinter import *

class FormGenerator:

    def __init__(self, form_name, form_fields):
        self.form = Toplevel()
        self.form_name = form_name
        self.form_fields = form_fields
        self.data = []

    def run(self):
        self.form.title(self.form_name)
        self.ents = self.makeform()
        self.makebutton()
        self.form.mainloop()
        return self.data

    def makeform(self):
        fields = {}
        for field in self.form_fields:
            row = Frame(self.form)
            lab = Label(row, width=22, text=field + ": ", anchor='w')
            ent = Entry(row)
            ent.insert(0, "0")
            row.pack(side=TOP, fill=X, padx=5, pady=5)
            lab.pack(side=LEFT)
            ent.pack(side=RIGHT, expand=YES, fill=X)
            fields[field] = ent
        return fields

    def makebutton(self):
        b1 = Button(self.form, text='Confirm',
                    command=(lambda e=self.ents: self.recordentry(e)))
        b1.pack(side=LEFT, padx=5, pady=5)
        b2 = Button(self.form, text='Quit',
                    command=self.form.destroy)
        b2.pack(side=LEFT, padx=5, pady=5)

    def recordentry(self, entries):
        for i in entries:
            self.data.append(entries[i].get())
        self.form.destroy()