import requests
from wxauto import WeChat
import os,sys,time,threading,json,pickle
from queue import Queue
import random
import ttkbootstrap as ttk
from openai import OpenAI
from dotenv import load_dotenv,find_dotenv
from tkinter import messagebox

class ChatApp():
    def __init__(self):
        self.wx = WeChat()
        self.sessions = []
        self.q= Queue()
        self.run = False
        self.processing = False
        self.session_history ={}
        self.triggers =['小妹','AI','ai','人工智能']
        self.load_settings()
        self.init_openai()
        self.init_ui()
        
        
    #在脚本同文件夹下寻找设置文件settings.pkl并加载，若无设置文件则创建默认值
    def load_settings(self):
        script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
        if not os.path.exists(script_directory+os.sep+'settings.pkl'):
            self.settings={
                'triggers':['助手','AI','ai','人工智能'],
                'whitelist':[],
                'instruction':'你是一个可爱的助手，你会认真回答所有问题，如果无法回答，则向对方提问，要求补全必要的信息',
                'examples':'',
                'max_tokens':4096,
               'model_name':'gpt-3.5-turbo-1106',
                'temperature':0.8,
                'join_rate':0.1
                }
            with open(script_directory+os.sep+'settings.pkl','wb') as f:
                pickle.dump(self.settings,f)
        with open(script_directory+os.sep+'settings.pkl','rb') as f:
            self.settings=pickle.load(f)

    def init_ui(self):
        '''创建GUI界面'''
        #首行标签
        self.root = ttk.Window(title='WeChat ChatBot')
        self.style = ttk.Style()
        self.style.theme_use('cyborg')
        self.trigger_label = ttk.Label(self.root,text='触发词（一行一个）').grid(row=1,column=1,padx=2,pady=2)
        self.whitelist_label = ttk.Label(self.root,text='白名单（一行一个）').grid(row=1,column=2,padx=2,pady=2)
        self.instruction_label = ttk.Label(self.root,text='系统提示').grid(row=1,column=3,columnspan=2,padx=2,pady=2)
        self.examples_label = ttk.Label(self.root,text='对话示例').grid(row=1,column=5,columnspan=2,padx=2,pady=2)
        #创建输入框
        self.trigger_input = ttk.ScrolledText(self.root,width=20)
        for trigger in self.settings['triggers']:
            self.trigger_input.insert(ttk.END,trigger+'\n')
        self.trigger_input.grid(row=2,column=1,columnspan=1,padx=2,pady=2)
        self.whitelist_input = ttk.ScrolledText(self.root,width=20)
        for name in self.settings['whitelist']:
            self.whitelist_input.insert(ttk.END,name+'\n')
        self.whitelist_input.grid(row=2,column=2,columnspan=1,padx=2,pady=2)
        self.instruction_input = ttk.ScrolledText(self.root,width=40)
        self.instruction_input.insert(ttk.END,self.settings['instruction'])
        self.instruction_input.grid(row=2,column=3,columnspan=2,padx=2,pady=2)
        self.examples_input = ttk.ScrolledText(self.root,width=40)
        self.examples_input.insert(ttk.END,self.settings['examples'])
        self.examples_input.grid(row=2,column=5,columnspan=2,padx=2,pady=2)
        #创建参数设置区
        self.model_name_label = ttk.Label(self.root,text='模型名称').grid(row=3,column=1,columnspan=1,padx=2,pady=2)
        self.model_name_input = ttk.Entry(self.root)
        self.model_name_input.insert(ttk.END,self.settings['model_name'])
        self.model_name_input.grid(row=3,column=2,columnspan=1,padx=2,pady=2,sticky='EW')
        self.temperature_label = ttk.Label(self.root,text='温度 0-2').grid(row=3,column=3,columnspan=1,padx=2,pady=2)
        self.temperature_entry = ttk.Entry(self.root)
        self.temperature_entry.insert(ttk.END,self.settings['temperature'])
        self.temperature_entry.grid(row=3,column=4,columnspan=1,padx=2,pady=2,sticky='EW')
        self.max_token_label = ttk.Label(self.root,text='最大token数').grid(row=4,column=1,columnspan=1,padx=2,pady=2)
        self.max_token_input = ttk.Entry(self.root)
        self.max_token_input.insert(ttk.END,self.settings['max_tokens'])
        self.max_token_input.grid(row=4,column=2,columnspan=1,padx=2,pady=2,sticky='EW')
        self.join_rate_label = ttk.Label(self.root,text='插话概率 0-1').grid(row=4,column=3,columnspan=1,padx=2,pady=2)
        self.join_rate_entry = ttk.Entry(self.root)
        self.join_rate_entry.insert(ttk.END,self.settings['join_rate'])
        self.join_rate_entry.grid(row=4,column=4,columnspan=1,padx=2,pady=2,sticky='EW')
        self.save_button = ttk.Button(self.root,text='保存并应用',command=self.apply_save_config)
        self.save_button.grid(row=3,rowspan=2,column=5,columnspan=2,padx=5,pady=5,sticky='EWNS')
        self.run_label = ttk.Label(self.root,text='未运行',font="-size 35 -weight bold")
        self.run_label.grid(row=5,column=1,columnspan=2,padx=2,pady=10)
        self.stop_button = ttk.Button(self.root,text='停止',command=self.stop,bootstyle='danger')
        self.start_button = ttk.Button(self.root,text='开始',command=self.start)
        self.stop_button.grid(row=5,column=3,columnspan=2,padx=2,pady=2,sticky='EWNS')
        self.start_button.grid(row=5,column=5,columnspan=2,padx=2,pady=2,sticky='EWNS')
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
        
    def apply_save_config(self):
        #检查trigger 列表，若为空，则self.triggers=['*']代表回复所有句子
        triggers=self.trigger_input.get("1.0", ttk.END).strip().split('\n')
        print(triggers)
        if triggers==['']:
            triggers=['*']
            self.trigger_input.insert(ttk.END,'*')
        #检查白名单，若为空，则self.whitelist=['*']代表不限制
        whitelist=self.whitelist_input.get("1.0", ttk.END).strip().split('\n')
        print(whitelist)
        if whitelist==['']:
            whitelist=['*']
            self.whitelist_input.insert(ttk.END,'*')
        instruction=self.instruction_input.get("1.0", ttk.END).strip()
        examples=self.examples_input.get("1.0", ttk.END).strip()
        model_name = self.model_name_input.get().strip()
        max_tokens = int(self.max_token_input.get().strip())
        temperature = float(self.temperature_entry.get().strip())
        if temperature>2:
            temperature=2
        elif temperature<0:
            temperature=0
        join_rate = float(self.join_rate_entry.get().strip())
        if join_rate>1:
            join_rate=1
        elif join_rate<0:
            join_rate=0
        self.settings={
            'triggers':triggers,
            'whitelist':whitelist,
            'instruction':instruction,
            'examples':examples,
           'model_name':model_name,
           'max_tokens':max_tokens,
            'temperature':temperature,
            'join_rate':join_rate
            }
        script_directory = os.path.dirname(os.path.abspath(sys.argv[0]))
        with open(script_directory+os.sep+'settings.pkl','wb') as f:
            pickle.dump(self.settings,f)
        
    def init_openai(self):
        _ = load_dotenv(find_dotenv())
        self.client = OpenAI()
    def triggered(self,question):
        if '*' in self.triggers:
            return True
        for trigger in self.settings['triggers']:
            if trigger in question:
                return True
    def rand_interested(self):
        if random.random()<self.settings['join_rate']:
            return True
        else:
            return False
    def get_new_message(self):
        while self.run:
            if self.processing:
                time.sleep(1)
                continue
            try:
                time.sleep(1)
                sessions=self.wx.GetSessionList()
                for session,n in sessions.items():
                    if n > 0:
                        self.wx.ChatWith(session)
                        msg_list = self.wx.GetAllMessage()
                        clean_list = [msg for msg in msg_list if msg[0] not in ['Time','SYS','Recall']]
                        msg=clean_list[-1]
                        msg = Msg(session,msg[0],msg[1])
                        self.q.put(msg)
            except Exception as e:
                print(e)
            time.sleep(1)

    def process_message(self):
        while self.run:
            msg:Msg = self.q.get()
            if msg:
                session = msg.session
                name = msg.name
                question = msg.question
                if not (session in self.settings['whitelist'] or '*' in self.settings['whitelist']):
                    continue
                print(f'Got message from {session}, {name}: {question}')
                if not self.session_history.get(session):
                    self.session_history[session]=[]
                self.session_history[session].append({
                "role": "user",
                "content": name+'说：'+question
                                })
                if len(self.session_history[session])>20:
                    self.session_history[session]=self.session_history[session][-20:]
                if not session == name:
                    if (not self.triggered(question)) and (not self.rand_interested()):
                        continue
                self.save_dialogue(session,question)
                self.processing = True
                try:
                    self.reply(session)
                except Exception as e:
                    print(e)
                self.processing = False
            time.sleep(0.1)

    def reply(self,session):
        messages= [{
            "role": "system",
            "content": self.settings['instruction']
        },
        {
            "role":"system",
            "content": "对话举例:\n"+self.settings['examples']
        }]
        messages.extend(self.session_history[session])
        response = self.client.chat.completions.create(model = self.settings['model_name'],
                                               max_tokens=self.settings['max_tokens'],
                                               temperature=self.settings['temperature'],
                                               messages=messages
                                               )
        answer = response.choices[0].message.content
        self.save_dialogue(session,answer)
        self.session_history[session].append(
        {
                "role": "assistant",
                "content": answer
            })
        self.wx.ChatWith(session)
        self.wx.SendMsg(answer)
    def start(self):
        print('Starting app')
        self.run = True
        self.get_new_message_thread = threading.Thread(target=self.get_new_message)
        self.process_message_thread= threading.Thread(target=self.process_message)
        self.get_new_message_thread.start()
        self.process_message_thread.start()
        print('Started\n')
        self.run_label.config(text='运行中')
    
    def stop(self):
        self.run = False
        # self.get_new_message_thread.join()
        # self.process_message_thread.join()
        self.run_label.config(text='已停止')    
    def save_dialogue(self,session,text):
        try:
            with open(session+'_history.txt','a',encoding='utf-8') as f:
                f.write(text+'\n')
        except Exception as e:
            print(e)
    
    def on_closing(self):
        if messagebox.askokcancel("请再次确认！", "确认退出？"):
            os._exit(1)

class Msg():
    def __init__(self,session,name,question):
        self.name = name
        self.session = session
        self.question = question

if __name__ == '__main__':
    app = ChatApp()
        
