import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
import pandas as pd
import re
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
from wordcloud import WordCloud
import string
import emoji

class ScrollableFrame(ttk.Frame):
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        
        # Create a canvas with a professional background
        self.canvas = tk.Canvas(self, bg='#f0f0f0')
        self.scrollbar = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollbar_x = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        
        # Create the scrollable frame with matching background
        self.scrollable_frame = ttk.Frame(self.canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set, xscrollcommand=self.scrollbar_x.set)
        
        self.scrollbar.pack(side="right", fill="y")
        self.scrollbar_x.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        self.bind_mouse_wheel()
        
    def bind_mouse_wheel(self):
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
            
        def _on_shift_mousewheel(event):
            self.canvas.xview_scroll(int(-1*(event.delta/120)), "units")
            
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.canvas.bind_all("<Shift-MouseWheel>", _on_shift_mousewheel)

class WhatsAppAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("WhatsApp Chat Analytics Dashboard")
        self.root.geometry("1400x900")
        self.root.configure(bg='#E6F3F5')  # Light turquoise background
        
        # Configure style
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#E6F3F5')
        self.style.configure('Header.TLabel', 
                           font=('Segoe UI', 24, 'bold'), 
                           background='#E6F3F5',
                           foreground='#40E0D0')  # Turquoise
        self.style.configure('SubHeader.TLabel', 
                           font=('Segoe UI', 12),
                           background='#E6F3F5',
                           foreground='#8B00FF')  # Violet
        self.style.configure('Dashboard.TButton',
                           font=('Segoe UI', 10, 'bold'),
                           padding=10,
                           background='#40E0D0')  # Turquoise
        
        # Create main frame
        main_frame = ttk.Frame(root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        main_frame.grid_rowconfigure(2, weight=1)
        main_frame.grid_columnconfigure(0, weight=1)
        
        # Header
        header_frame = ttk.Frame(main_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(header_frame, 
                 text="WhatsApp Chat Analytics Dashboard",
                 style='Header.TLabel').pack(side=tk.LEFT)
        
        # File selection frame with modern styling
        file_frame = ttk.Frame(main_frame)
        file_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 20))
        
        ttk.Label(file_frame, 
                 text="Select Chat File:",
                 style='SubHeader.TLabel').pack(side=tk.LEFT, padx=(0, 10))
        
        self.file_path = tk.StringVar()
        entry = ttk.Entry(file_frame, textvariable=self.file_path, width=50)
        entry.pack(side=tk.LEFT, padx=5)
        
        browse_btn = ttk.Button(file_frame, 
                              text="Browse",
                              style='Dashboard.TButton',
                              command=self.browse_file)
        browse_btn.pack(side=tk.LEFT, padx=5)
        
        analyze_btn = ttk.Button(file_frame,
                               text="Analyze Chat",
                               style='Dashboard.TButton',
                               command=self.analyze_chat)
        analyze_btn.pack(side=tk.LEFT, padx=5)
        
        # Create notebook with custom styling
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Style the notebook
        self.style.configure('TNotebook', background='#f0f0f0')
        self.style.configure('TNotebook.Tab', 
                           padding=[12, 8],
                           font=('Segoe UI', 10))
        
        # Messages Table tab
        text_frame = ttk.Frame(self.notebook)
        self.notebook.add(text_frame, text="Messages")
        
        # Create table with custom styling
        table_container = ttk.Frame(text_frame)
        table_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create Treeview for messages table
        self.tree = ttk.Treeview(table_container, 
                                columns=('User', 'Message', 'Time', 'Date'),
                                show='headings',
                                selectmode='browse')
        
        # Style the Treeview
        style = ttk.Style()
        style.configure("Treeview", 
                       background="white",
                       foreground="#2c3e50",
                       fieldbackground="white",
                       rowheight=25,
                       font=('Segoe UI', 10))
        
        style.configure("Treeview.Heading",
                       background="#40E0D0",
                       foreground="#8B00FF",
                       font=('Segoe UI', 11, 'bold'),
                       relief="flat")
        
        style.map("Treeview.Heading",
                 background=[('active', '#48D1CC')])
        
        # Configure columns for messages table
        self.tree.heading('User', text='User', anchor=tk.W)
        self.tree.heading('Message', text='Message', anchor=tk.W)
        self.tree.heading('Time', text='Time', anchor=tk.W)
        self.tree.heading('Date', text='Date', anchor=tk.W)
        
        self.tree.column('User', width=150, minwidth=150)
        self.tree.column('Message', width=500, minwidth=300)
        self.tree.column('Time', width=100, minwidth=100)
        self.tree.column('Date', width=150, minwidth=150)
        
        # Add scrollbars for messages table
        vsb = ttk.Scrollbar(table_container, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_container, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        
        # Grid layout for messages table
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights for messages table
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Emoji Analysis tab
        emoji_frame = ttk.Frame(self.notebook)
        self.notebook.add(emoji_frame, text="Emoji Analysis")
        
        # Create table container for emoji analysis
        emoji_table_container = ttk.Frame(emoji_frame)
        emoji_table_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create Treeview for emoji table
        self.emoji_tree = ttk.Treeview(emoji_table_container,
                                     show='headings',
                                     selectmode='browse')
        
        # Add scrollbars for emoji table
        emoji_vsb = ttk.Scrollbar(emoji_table_container, orient="vertical", command=self.emoji_tree.yview)
        emoji_hsb = ttk.Scrollbar(emoji_table_container, orient="horizontal", command=self.emoji_tree.xview)
        self.emoji_tree.configure(yscrollcommand=emoji_vsb.set, xscrollcommand=emoji_hsb.set)
        
        # Grid layout for emoji table
        self.emoji_tree.grid(row=0, column=0, sticky='nsew')
        emoji_vsb.grid(row=0, column=1, sticky='ns')
        emoji_hsb.grid(row=1, column=0, sticky='ew')
        
        # Configure grid weights for emoji table
        emoji_table_container.grid_rowconfigure(0, weight=1)
        emoji_table_container.grid_columnconfigure(0, weight=1)
        
        # Visualizations tab
        self.viz_frame = ScrollableFrame(self.notebook)
        self.notebook.add(self.viz_frame, text="Visualizations")
        self.viz_canvas = None
        
        # Configure root grid
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)

    def preprocess(self, chat_file):
        try:
            with open(chat_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract messages using regex
            pattern = r'(\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s(?:AM|PM))\s-\s(.+?)(?=\n\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}\s(?:AM|PM)\s-\s|$)'
            matches = re.findall(pattern, content, re.DOTALL)
            
            if not matches:
                raise ValueError("No messages found in the chat file. Please check the file format.")
            
            # Process messages
            data = []
            for date_str, message in matches:
                # Split user and message
                if ':' in message:
                    user, msg = message.split(':', 1)
                else:
                    user = 'System'
                    msg = message
                
                data.append({
                    'DATE': date_str,
                    'USER': user.strip(),
                    'MESSAGE': msg.strip()
                })
            
            # Create DataFrame
            df = pd.DataFrame(data)
            
            # Convert date string to datetime
            df['DATE'] = pd.to_datetime(df['DATE'], format='%m/%d/%y, %I:%M %p')
            
            return df
            
        except Exception as e:
            raise Exception(f"Error processing file: {str(e)}")

    def create_visualizations(self, df):
        try:
            if self.viz_canvas:
                self.viz_canvas.get_tk_widget().destroy()
            
            # Set style for attractive visualizations
            plt.rcParams['axes.grid'] = True
            plt.rcParams['grid.alpha'] = 0.3
            plt.rcParams['axes.facecolor'] = '#ffffff'
            plt.rcParams['figure.facecolor'] = '#E6F3F5'
            plt.rcParams['font.family'] = 'Segoe UI'
            
            # Create figure with subplots (7 plots now, including word cloud)
            fig = Figure(figsize=(15, 14), dpi=100)
            fig.patch.set_facecolor('#E6F3F5')
            
            # Custom color palettes
            user_colors = ['#40E0D0', '#8B00FF', '#00CED1', '#9370DB', '#48D1CC', '#9932CC']
            type_colors = ['#E0FFFF', '#E6E6FA', '#AFEEEE', '#D8BFD8', '#B0E0E6', '#DDA0DD']
            
            # Create a GridSpec to have better control over subplot sizes
            gs = fig.add_gridspec(4, 2, height_ratios=[1, 1, 1, 1.2])
            
            # 1. Messages by User (Pie Chart)
            ax1 = fig.add_subplot(gs[0, 0])
            ax1.set_facecolor('#ffffff')
            user_counts = df['USER'].value_counts()
            wedges, texts, autotexts = ax1.pie(user_counts.values, 
                                             labels=user_counts.index, 
                                             autopct='%1.1f%%',
                                             colors=user_colors[:len(user_counts)],
                                             shadow=True)
            ax1.set_title('Message Distribution by User', 
                         pad=20, 
                         fontsize=12, 
                         fontweight='bold',
                         color='#40E0D0')
            
            # Style for all other plots
            title_color = '#40E0D0'  # Turquoise
            label_color = '#8B00FF'  # Violet
            
            # 2. Message Types by User (Stacked Bar Chart)
            ax2 = fig.add_subplot(gs[0, 1])
            ax2.set_facecolor('#ffffff')
            message_types = pd.crosstab(df['USER'], df['MESSAGE'].apply(self.get_message_type))
            bottom = np.zeros(len(message_types.index))
            
            for i, col in enumerate(message_types.columns):
                ax2.bar(message_types.index, 
                       message_types[col], 
                       bottom=bottom,
                       label=col, 
                       color=type_colors[i % len(type_colors)])
                bottom += message_types[col]
            
            ax2.set_title('Message Types by User', fontsize=12, fontweight='bold', color=title_color)
            ax2.tick_params(axis='x', rotation=30, colors=label_color)
            ax2.set_ylabel('Count', color=label_color)
            ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax2.grid(True, alpha=0.3)
            
            # 3. Activity by Hour (Line Plot)
            ax3 = fig.add_subplot(gs[1, 0])
            ax3.set_facecolor('#ffffff')
            df['Hour'] = df['DATE'].dt.hour
            
            for i, user in enumerate(df['USER'].unique()):
                user_data = df[df['USER'] == user]
                hourly_activity = user_data['Hour'].value_counts().sort_index()
                hours = range(24)
                counts = [hourly_activity.get(hour, 0) for hour in hours]
                ax3.plot(hours, 
                        counts, 
                        marker='o', 
                        linestyle='-', 
                        linewidth=2,
                        label=user, 
                        color=user_colors[i % len(user_colors)])
            
            ax3.set_title('Activity by Hour (Per User)', fontsize=12, fontweight='bold', color=title_color)
            ax3.set_xlabel('Hour of Day', color=label_color)
            ax3.set_ylabel('Number of Messages', color=label_color)
            ax3.tick_params(colors=label_color)
            ax3.set_xticks(range(0, 24, 2))
            ax3.grid(True, alpha=0.3)
            ax3.legend()
            
            # 4. Messages by Month
            ax4 = fig.add_subplot(gs[1, 1])
            ax4.set_facecolor('#ffffff')
            df['Month'] = pd.Categorical(df['DATE'].dt.strftime('%B'),
                                       categories=['January', 'February', 'March', 'April', 'May', 'June',
                                                 'July', 'August', 'September', 'October', 'November', 'December'],
                                       ordered=True)
            monthly_by_user = pd.crosstab(df['Month'], df['USER'])
            
            x = np.arange(len(monthly_by_user.index))
            width = 0.35
            n_users = len(monthly_by_user.columns)
            
            for i, user in enumerate(monthly_by_user.columns):
                offset = width * (i - (n_users-1)/2)
                ax4.bar(x + offset, 
                       monthly_by_user[user], 
                       width, 
                       label=user,
                       color=user_colors[i % len(user_colors)])
            
            ax4.set_title('Messages by Month (Per User)', fontsize=12, fontweight='bold', color=title_color)
            ax4.set_xticks(x)
            ax4.set_xticklabels(monthly_by_user.index, rotation=45, color=label_color)
            ax4.set_ylabel('Number of Messages', color=label_color)
            ax4.tick_params(colors=label_color)
            ax4.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
            ax4.grid(True, alpha=0.3)
            
            # 5. Daily Activity Patterns (Heatmap)
            ax5 = fig.add_subplot(gs[2, 0])
            ax5.set_facecolor('#ffffff')
            df['DayNum'] = df['DATE'].dt.dayofweek
            pivot_table = pd.crosstab(df['DayNum'], df['Hour'])
            
            im = ax5.imshow(pivot_table.values, 
                          cmap='RdPu',  # Purple-based colormap
                          aspect='auto',
                          interpolation='nearest')
            fig.colorbar(im, ax=ax5, label='Number of Messages')
            
            ax5.set_title('Activity Heatmap (Day vs Hour)', fontsize=12, fontweight='bold', color=title_color)
            ax5.set_ylabel('Day of Week', color=label_color)
            ax5.set_xlabel('Hour of Day', color=label_color)
            ax5.set_yticks(range(7))
            ax5.set_yticklabels(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'],
                               color=label_color)
            ax5.set_xticks(range(0, 24, 2))
            ax5.tick_params(colors=label_color)
            
            # 6. Message Length Distribution
            ax6 = fig.add_subplot(gs[2, 1])
            ax6.set_facecolor('#ffffff')
            df['MessageLength'] = df['MESSAGE'].str.len()
            
            data = [df[df['USER'] == user]['MessageLength'] for user in df['USER'].unique()]
            bp = ax6.boxplot(data, 
                           labels=df['USER'].unique(),
                           patch_artist=True,
                           medianprops=dict(color="#40E0D0"),  # Turquoise median line
                           flierprops=dict(marker='o', markerfacecolor='#8B00FF'))  # Violet outliers
            
            # Color each box
            for i, box in enumerate(bp['boxes']):
                box.set(facecolor=user_colors[i % len(user_colors)])
            
            ax6.set_title('Message Length Distribution by User', fontsize=12, fontweight='bold', color=title_color)
            ax6.set_ylabel('Message Length (characters)', color=label_color)
            ax6.tick_params(axis='x', rotation=30, colors=label_color)
            ax6.grid(True, alpha=0.3)
            
            # 7. Word Cloud
            ax7 = fig.add_subplot(gs[3, :])
            ax7.set_facecolor('#ffffff')
            
            # Prepare text for word cloud
            def clean_text(text):
                # Convert to lowercase and remove punctuation
                text = text.lower()
                text = text.translate(str.maketrans('', '', string.punctuation))
                # Remove common WhatsApp words and short words
                stop_words = {'media', 'omitted', 'message', 'deleted', 'http', 'https', 'www', 'com'}
                words = text.split()
                words = [word for word in words if word not in stop_words and len(word) > 2]
                return ' '.join(words)
            
            # Combine all messages and clean the text
            all_text = ' '.join(df['MESSAGE'].astype(str))
            cleaned_text = clean_text(all_text)
            
            # Create and generate word cloud
            wordcloud = WordCloud(
                width=1200,
                height=400,
                background_color='white',
                colormap='PuBu',  # Purple-Blue colormap
                max_words=100,
                contour_width=3,
                contour_color='#40E0D0'  # Turquoise border
            ).generate(cleaned_text)
            
            # Display word cloud
            ax7.imshow(wordcloud, interpolation='bilinear')
            ax7.set_title('Most Common Words in Chat', 
                         fontsize=12, 
                         fontweight='bold',
                         color='#40E0D0',
                         pad=20)
            ax7.axis('off')
            
            # Adjust layout
            fig.tight_layout(pad=3.0)
            
            # Create canvas with custom styling
            canvas = FigureCanvasTkAgg(fig, master=self.viz_frame.scrollable_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            self.viz_canvas = canvas
            
        except Exception as e:
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"Error creating visualizations: {str(e)}")
            raise e

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Select WhatsApp Chat File",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if filename:
            self.file_path.set(filename)

    def get_message_type(self, message):
        if pd.isna(message):
            return "Empty"
        message = str(message).strip()
        if message == "<Media omitted>":
            return "Media"
        elif "http" in message.lower() or "www." in message.lower():
            return "Link"
        elif "missed voice call" in message.lower():
            return "Missed Call"
        elif "this message was deleted" in message.lower():
            return "Deleted"
        else:
            return "Text"

    def get_emoji_counts(self, df):
        emoji_counts = {}
        users = df['USER'].unique()
        
        # Initialize emoji counts for each user
        for user in users:
            emoji_counts[user] = {}
        
        # Count emojis for each user
        for _, row in df.iterrows():
            message = row['MESSAGE']
            user = row['USER']
            
            # Extract emojis from message
            emojis_in_msg = [c for c in message if emoji.is_emoji(c)]
            
            # Update counts
            for em in emojis_in_msg:
                if em not in emoji_counts[user]:
                    emoji_counts[user][em] = 0
                emoji_counts[user][em] += 1
        
        # Convert to DataFrame
        emoji_data = []
        all_emojis = set()
        
        # Get all unique emojis
        for user_counts in emoji_counts.values():
            all_emojis.update(user_counts.keys())
        
        # Create rows for DataFrame
        for emoji_char in all_emojis:
            row = {'Emoji': emoji_char}
            for user in users:
                row[user] = emoji_counts[user].get(emoji_char, 0)
            emoji_data.append(row)
        
        return pd.DataFrame(emoji_data)

    def update_emoji_table(self, emoji_df):
        # Configure columns
        columns = ['Emoji'] + list(emoji_df.columns[2:])  # First column is emoji, rest are users
        self.emoji_tree['columns'] = columns
        print(columns)
        
        # Set column headings
        for col in columns:
            self.emoji_tree.heading(col, text=col, anchor=tk.CENTER)
            self.emoji_tree.column(col, width=100, minwidth=100, anchor=tk.CENTER)
        
        # Clear existing items
        self.emoji_tree.delete(*self.emoji_tree.get_children())
        
        # Insert data
        for idx, row in emoji_df.iterrows():
            values = [row[col] for col in columns]
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.emoji_tree.insert('', 'end', values=values, tags=(tag,))
        
        # Configure row colors
        self.emoji_tree.tag_configure('oddrow', background='#E6F3F5')  # Light turquoise
        self.emoji_tree.tag_configure('evenrow', background='#F5E6F3')  # Light violet

    def analyze_chat(self):
        file_path = self.file_path.get()
        if not file_path:
            self.tree.delete(*self.tree.get_children())
            self.tree.insert('', 'end', values=('Error', 'Please select a chat file first!', '', ''))
            return
        
        try:
            # Read and process the chat
            df = self.preprocess(file_path)
            
            # Clear existing items in messages table
            self.tree.delete(*self.tree.get_children())
            
            # Format the data for messages table
            for index, row in df.iterrows():
                time_str = row['DATE'].strftime('%I:%M:%S %p')
                date_str = row['DATE'].strftime('%B %d, %Y')
                
                tag = 'evenrow' if index % 2 == 0 else 'oddrow'
                self.tree.insert('', 'end',
                               values=(row['USER'],
                                     row['MESSAGE'],
                                     time_str,
                                     date_str),
                               tags=(tag,))
            
            # Configure row colors for messages table
            self.tree.tag_configure('oddrow', background='#E6F3F5')
            self.tree.tag_configure('evenrow', background='#F5E6F3')
            
            # Update emoji analysis table
            emoji_df = self.get_emoji_counts(df)
            self.update_emoji_table(emoji_df)
            
            # Create visualizations
            self.create_visualizations(df)
            
        except Exception as e:
            self.tree.delete(*self.tree.get_children())
            self.tree.insert('', 'end', values=('Error', f'Error analyzing chat: {str(e)}', '', ''))

def main():
    root = tk.Tk()
    app = WhatsAppAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main() 