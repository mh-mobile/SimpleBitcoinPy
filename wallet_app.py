import binascii
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from tkinter import ttk
from tkinter.ttk import Button, Style

from utils.key_manager import KeyManager
import os


class SimpleBC_Gui(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)
        self.parent = parent
        self.parent.protocol('WM_DELETE_WINDOW', self.quit)
        self.coin_balance = StringVar(self.parent, '0')
        self.status_message = StringVar(self.parent, 'No coin to be sent')
        self.initApp()
        self.setupGUI()

    def quit(self, event=None):
        self.parent.destroy()

    def initApp(self):
        print('SimpleBitcoin client is now activating...')
        self.km = KeyManager()

    def display_info(self, info):
        pass

    def update_status(self, info):
        self.status_message.set(info)

    def update_balance(self):
        pass

    def create_menu(self):
        top = self.winfo_toplevel()
        self.menuBar = Menu(top)
        top['menu'] = self.menuBar

        self.subMenu = Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label='Menu', menu=self.subMenu)
        self.subMenu.add_command(
            label='Show My Address', command=self.show_my_address)
        self.subMenu.add_command(
            label='Load my Keys', command=self.show_input_dialog_for_key_loading)
        self.subMenu.add_command(
            label='Update Blockchain', command=self.update_block_chain)
        self.subMenu.add_separator()
        self.subMenu.add_command(label='Quit', command=self.quit)
        self.subMenu2 = Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label='Settings', menu=self.subMenu2)
        self.subMenu2.add_command(
            label='Renew my Keys', command=self.renew_my_keypairs)
        self.subMenu2.add_command(
            label='Connection Info', command=self.edit_conn_info)
        self.subMenu3 = Menu(self.menuBar, tearoff=0)
        self.menuBar.add_cascade(label='Advance', menu=self.subMenu3)
        self.subMenu3.add_command(
            label='Show logs', command=self.open_log_window)
        self.subMenu3.add_command(
            label='Show Blockchain', command=self.show_my_block_chain)

    def show_my_address(self):
        f = Tk()
        label = Label(f, text='My Address')
        label.pack()
        key_info = Text(f, width=70, height=10)
        my_address = self.km.my_address()
        key_info.insert(INSERT, my_address)
        key_info.pack()

    def update_block_chain(self):
        pass

    def show_input_dialog_for_key_loading(self):
        def load_my_keys():
            # ファイル選択ダイアログの表示
            f2 = Tk()
            f2.withdraw()
            fTyp = [('', '*.pem')]
            iDir = os.path.abspath(os.path.dirname(__file__))
            messagebox.showinfo(
                'Load key pair', 'please choose your key file')
            f_name = filedialog.askopenfilename(
                filetypes=fTyp, initialdir=iDir)

            try:
                file = open(f_name)
                data = file.read()
                target = binascii.unhexlify(data)
                self.km.import_key_pair(target, entry1.get())
            except Exception as e:
                print(e)
            finally:
                file.close()
                f.destroy()
                f2.destroy()
                # self.um = UTXM(self.km.my_address())
                # self.um.my_balance = 0
                # self.update_balance()

        f = Tk()
        label0 = Label(
            f, text='Please enter pass phrase for your key pair')
        frame1 = ttk.Frame(f)
        label1 = ttk.Label(frame1, text='Pass Phrase:')

        entry1 = ttk.Entry(frame1)
        button1 = ttk.Button(frame1, text='Load', command=load_my_keys)

        label0.grid(row=0, column=0, sticky=(N, E, S, W))
        frame1.grid(row=1, column=0, sticky=(N, E, S, W))
        label1.grid(row=2, column=0, sticky=E)
        entry1.grid(row=2, column=1, sticky=W)
        button1.grid(row=3, column=1, sticky=W)

    def renew_my_keypairs(self):
        def save_my_pem():
            self.km = KeyManager()
            my_pem = self.km.export_key_pair(entry1.get())
            my_pem_hex = binascii.hexlify(my_pem).decode('ascii')
            # とりあえずファイル名は固定
            path = 'my_key_pair.pem'
            f1 = open(path, 'a')
            f1.write(my_pem_hex)
            f1.close()

            f.destroy()
            # self.um = UTXM(self.km.my_address())
            # self.um.my_balance = 0
            # self.update_balance()

        f = Tk()
        f.title('New Key Gene')
        label0 = Label(
            f, text='Please enter pass phrase for your new key pair')
        frame1 = ttk.Frame(f)
        label1 = ttk.Label(frame1, text='Pass Phrase:')

        entry1 = ttk.Entry(frame1)
        button1 = ttk.Button(frame1, text='Generate', command=save_my_pem)

        label0.grid(row=0, column=0, sticky=(N, E, S, W))
        frame1.grid(row=1, column=0, sticky=(N, E, S, W))
        label1.grid(row=2, column=0, sticky=E)
        entry1.grid(row=2, column=1, sticky=W)
        button1.grid(row=3, column=1, sticky=W)

    def edit_conn_info(self):
        pass

    def open_log_window(self):
        pass

    def show_my_block_chain(self):
        pass

    def setupGUI(self):
        self.parent.bind('<Control-q>', self.quit)
        self.parent.title('SimpleBitcoin GUI')
        self.pack(fill=BOTH, expand=1)

        self.create_menu()

        lf = LabelFrame(self, text='Current Balance')
        lf.pack(side=TOP, fill='both', expand='yes', padx=7, pady=7)

        lf2 = LabelFrame(self, text='')
        lf2.pack(side=BOTTOM, fill='both', expand='yes', padx=7, pady=7)

        self.balance = Label(
            lf, textvariable=self.coin_balance, font='Helvetica 20')
        self.balance.pack()

        self.label = Label(lf2, text='Recipient Address:')
        self.label.grid(row=0, pady=5)

        self.recipient_pubkey = Entry(lf2, bd=2)
        self.recipient_pubkey.grid(row=0, column=1, pady=5)

        self.label2 = Label(lf2, text='Amount to pay : ')
        self.label2.grid(row=1, pady=5)

        self.amoutBox = Entry(lf2, bd=2)
        self.amoutBox.grid(row=1, column=1, pady=5, sticky='NSEW')

        self.label3 = Label(lf2, text='Fee (Optional) :')
        self.label3.grid(row=2, pady=5)

        self.amoutBox2 = Entry(lf2, bd=2)
        self.amoutBox2.grid(row=2, column=1, pady=5, sticky='NSEW')

        self.label4 = Label(lf2, text='')
        self.label4.grid(row=3, pady=5)

        self.sendBtn = Button(lf2, text='\nSend Coin(s)\n',
                              command=self.sendCoins)
        self.sendBtn.grid(row=4, column=1, sticky='NSEW')

        stbar = Label(self.winfo_toplevel(
        ), textvariable=self.status_message, bd=1, relief=SUNKEN, anchor=W)
        stbar.pack(side=BOTTOM, fill=X)

    def sendCoins(self):
        pass


def main():
    root = Tk()
    app = SimpleBC_Gui(root)
    root.mainloop()


if __name__ == '__main__':
    main()
