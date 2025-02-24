import tkinter as tk
from tkinter import scrolledtext, simpledialog
import ttkbootstrap as tb
import sqlite3
import requests
from bs4 import BeautifulSoup
from googlesearch import search
import time
import webbrowser
import speech_recognition as sr
import psutil
import os
import signal

class alGORErythm:
    def __init__(self):
        # Database setup
        self.conn = sqlite3.connect('chat_history.db')
        self.c = self.conn.cursor()
        self.c.execute('''CREATE TABLE IF NOT EXISTS chat_history (input TEXT, output TEXT)''')
        self.conn.commit()
        
        # Initialize Tkinter
        self.root = tb.Window(themename="cosmo")
        self.root.title("AI Internet Scraper")
        self.root.geometry("2200x1800")  # Adjusted for better layout

        # Setting global styles before adding widgets
        self.root.configure(bg='lightblue')
        self.root.option_add('*Button.Background', 'orange')
        self.root.option_add('*Button.Foreground', 'black')

        # Mode variable
        self.mode = tk.StringVar(value="Precise Mode")

        # Frame setup
        self.left_top_frame = tk.Frame(self.root, bg='lightblue', width=600, height=400)
        self.left_top_frame.grid(row=0, column=0, sticky="nsew")
        
        self.right_top_frame = tk.Frame(self.root, bg='lemonchiffon', width=600, height=400)
        self.right_top_frame.grid(row=0, column=1, sticky="nsew")
        
        self.left_bottom_frame = tk.Frame(self.root, bg='lightblue', width=600, height=400)
        self.left_bottom_frame.grid(row=1, column=0, sticky="nsew")
        
        self.right_bottom_frame = tk.Frame(self.root, bg='lightblue', width=600, height=400)
        self.right_bottom_frame.grid(row=1, column=1, sticky="nsew")
        
        # Configure grid layout
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        
        # GUI components
        self.text_box = scrolledtext.ScrolledText(self.left_top_frame, width=80, height=25, wrap=tk.WORD, state='disabled', bg='lemonchiffon')
        self.text_box.pack(pady=10)
        
        self.tree = tb.Treeview(self.right_top_frame)
        self.tree.pack(expand=True, fill=tk.BOTH)
        
        self.input_frame = tk.Frame(self.right_bottom_frame, bg='lightblue')
        self.input_frame.pack()
        self.text_input = tk.Entry(self.input_frame, width=70)
        self.text_input.pack(side="left", pady=20)
        
        self.send_button = tk.Button(self.input_frame, text="Send", command=lambda: self.handle_input(self.text_input.get()))
        self.send_button.pack(side="right")
        
        self.button_frame = tk.Frame(self.left_bottom_frame, bg='lightblue')
        self.button_frame.pack(side="top", anchor="w")
        
        self.mic_button = tk.Button(self.button_frame, text="🎤", command=self.record_audio)
        self.mic_button.pack(side="top", padx=5, pady=5)
        
        self.plus_button = tk.Button(self.button_frame, text="+", command=lambda: self.handle_input(self.text_input.get()))
        self.plus_button.pack(side="top", padx=5, pady=5)
        
        self.r_button = tk.Button(self.button_frame, text="R", command=lambda: self.handle_input(self.text_input.get()))
        self.r_button.pack(side="top", padx=5, pady=5)
        
        self.p_button = tk.Button(self.button_frame, text="P", command=lambda: self.handle_input(self.text_input.get()))
        self.p_button.pack(side="top", padx=5, pady=5)
        
        self.toggle_button = tk.Button(self.button_frame, textvariable=self.mode, command=self.toggle_mode)
        self.toggle_button.pack(side="top", padx=5, pady=5)
        
        # Load chat history or ask for user's name
        self.c.execute("SELECT * FROM chat_history")
        self.chat_history = self.c.fetchall()
        if not self.chat_history:
            self.user_name = simpledialog.askstring("Input", "What's your name?")
        else:
            self.user_name = "Jonathan"
        
        print("Running main loop")
        self.root.mainloop()

        print("Closing database connection")
        self.conn.close()

    def apply_background_color(self, parent, color='lightblue'):
        for widget in parent.winfo_children():
            if isinstance(widget, (tk.Frame, tk.Label, tk.Button)):
                widget.configure(bg=color)
            self.apply_background_color(widget, color)

    def clean_text(self, text):
        return ' '.join(word.lower().strip(",.!?") for word in text.split() if word.isalnum())

    def bing_search(self, query):
        url = "https://www.bing.com/search"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        params = {
            'q': query,
            'count': '10'  # Number of search results per page
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('li', {'class': 'b_algo'})
            search_results = []
            for result in results:
                title = result.find('h2').text
                link = result.find('a')['href']
                snippet = result.find('p').text
                search_results.append((title, link, snippet))
            return search_results
        else:
            print("Failed to retrieve search results")
            return []

    def duckduckgo_search(self, query):
        url = "https://duckduckgo.com/html/"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
        }
        params = {
            'q': query
        }
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('a', {'class': 'result__a'})
            search_results = []
            for result in results:
                title = result.text
                link = result['href']
                snippet = result.find_next('a', {'class': 'result__snippet'}).text if result.find_next('a', {'class': 'result__snippet'}) else 'No snippet available'
                search_results.append((title, link, snippet))
            return search_results
        else:
            print("Failed to retrieve search results")
            return []

    def update_output(self, ai_output):
        self.text_box.config(state='normal')
        self.text_box.insert(tk.END, ai_output + "\n")
        self.text_box.config(state='disabled')

    def scrape_url(self, search_query):
        search_engines = ["google", "bing", "duckduckgo"]
        engine_index = 0
        results = []

        for _ in range(10):  # Run through the search engines 10 times
            engine = search_engines[engine_index]
            engine_index = (engine_index + 1) % len(search_engines)
            try:
                if engine == "google":
                    search_results = search(f"{search_query} site:{self.mode.get()}", num_results=15, lang="en")
                elif engine == "bing":
                    search_results = self.bing_search(search_query)
                elif engine == "duckduckgo":
                    search_results = self.duckduckgo_search(search_query)
                
                for result in search_results:
                    if not isinstance(result, str):
                        result = result[1]  # Access the URL part of the tuple
                    if not result.startswith(("http://", "https://")):
                        result = "https://" + result  # Prepend scheme if missing
                    print(f"Scraped URL: {result}")
                    response = requests.get(result)
                    soup = BeautifulSoup(response.text, 'html.parser')
                    paragraphs = soup.find_all('p')
                    human_readable_text = ' '.join(paragraph.text for paragraph in paragraphs if paragraph.text)
                    if human_readable_text:
                        print(f"Extracted Text: {human_readable_text[:500]}")
                        results.append((result, human_readable_text[:500]))
                time.sleep(2.5)  # Wait 2.5 seconds between queries
            except Exception as e:
                print(f"Error scraping with {engine}: {e}")
                continue
        return results if results else "No results found"

    def save_results_to_db(self, user_input, results):
        for url, content in results:
            self.c.execute("INSERT INTO chat_history (input, output) VALUES (?, ?)", (user_input, f"{url}: {content}"))
        self.conn.commit()

    def update_tree_view(self, results):
        self.tree.delete(*self.tree.get_children())
        
        domain_nodes = {}
        for url, content in results:
            domain = url.split("/")[2]
            if domain not in domain_nodes:
                domain_nodes[domain] = self.tree.insert('', 'end', text=domain, open=False)
            self.tree.insert(domain_nodes[domain], 'end', text=url, values=(url,), open=False)
        
        self.tree.bind('<Double-1>', self.on_tree_item_double_click)

    def on_tree_item_double_click(self, event):
        item = self.tree.selection()[0]
        url = self.tree.item(item, "text")
        webbrowser.open(url)

    def handle_input(self, user_input):
        if user_input:
            cleaned_input = self.clean_text(user_input)
            print(f"Cleaned Input: {cleaned_input}")
            results = self.scrape_url(cleaned_input)

            if isinstance(results, str):
                ai_output = f"Here's what I found: {results}"
                self.update_output(ai_output)
                return

            ai_output = "Here's what I found:\n"
            for url, content in results:
                ai_output += f"{url}: {content}\n"
            
            self.save_results_to_db(user_input, results)
            self.update_output(ai_output)
            print(f"AI Output: {ai_output}")

            self.text_input.delete(0, tk.END)

            # Update tree view
            self.update_tree_view(results)
        else:
            print("No input provided")

    def record_audio(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            print("Recording...")
            audio = recognizer.listen(source)
            print("Recording finished.")
        try:
            text = recognizer.recognize_google(audio)
            self.handle_input(text)
        except sr.UnknownValueError:
            print("Google Speech Recognition could not understand audio")
        except sr.RequestError as e:
            print(f"Could not request results from Google Speech Recognition service; {e}")
   
    def toggle_mode(self):
        self.mode.set("Relaxed Mode" if self.mode.get() == "Precise Mode" else "Precise Mode")

    def on_closing(self):
        # Terminate the parent terminal process
        parent_pid = psutil.Process(os.getpid()).ppid()
        os.kill(parent_pid, signal.SIGTERM)
        # Close the Tkinter window
        self.destroy()

if __name__ == "__main__":
    app = alGORErythm()
    app.root.mainloop()

