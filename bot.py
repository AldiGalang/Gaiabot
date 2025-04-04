import aiohttp, asyncio, random
from aiohttp_socks import ProxyConnector
from colorama import init, Fore

init(autoreset=True)

# Fungsi untuk memuat API Keys dari file
def load_api_keys(file_path):
    try:
        with open(file_path, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"{Fore.LIGHTRED_EX}🚨 File {file_path} not found!")
        return []

# Fungsi untuk memuat proxy dari file
def load_proxies(file_path):
    try:
        with open(file_path, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"{Fore.LIGHTRED_EX}🚨 File {file_path} not found!")
        return []

# Fungsi untuk memuat pertanyaan dari file
def load_questions(file_path):
    try:
        with open(file_path, "r") as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"{Fore.LIGHTRED_EX}🚨 File {file_path} not found!")
        return []

# Memuat data dari file
API_KEYS = load_api_keys("file_api_keys.txt")
PROXIES = load_proxies("proxy.txt")  # Proxy format: user:pass@host:port
QUESTIONS = load_questions("file_questions.txt")

domain_input = "optimize.gaia.domains"
URLS = [domain_input]
print(f"{Fore.LIGHTCYAN_EX}📌 Using domain: {domain_input}")

if not API_KEYS or not QUESTIONS or not PROXIES:
    print(f"{Fore.LIGHTRED_EX}🚨 Missing required data (API Keys, Questions, or Proxies). Program is stopping!")
    exit()

class ChatBot:
    def __init__(self):
        self.api_key_index = 0
        self.proxy_index = 0

    def get_next_api_key(self):
        api_key = API_KEYS[self.api_key_index]
        self.api_key_index = (self.api_key_index + 1) % len(API_KEYS)
        return api_key
    
    def get_next_proxy(self):
        proxy = PROXIES[self.proxy_index]  # Format user:pass@host:port
        self.proxy_index = (self.proxy_index + 1) % len(PROXIES)
        return proxy

    async def send_question(self, question: str, max_retries=5):
        retries = 0
        while retries < max_retries:  
            api_key = self.get_next_api_key()
            proxy = self.get_next_proxy()
            base_url = URLS[0]  
            
            data = {
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": question}
                ]
            }

            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }

            proxy_url = f"http://{proxy}"
            connector = ProxyConnector.from_url(proxy_url)
            
            async with aiohttp.ClientSession(connector=connector) as session:
                try:
                    async with session.post(f"https://{base_url}/v1/chat/completions", headers=headers, json=data, timeout=120) as response:
                        response.raise_for_status()
                        result = await response.json()
                        answer = result["choices"][0]["message"]["content"]
                        
                        word_count = len(answer.split())  # Hitung jumlah kata
                        
                        print(f"{Fore.LIGHTCYAN_EX}🌍 Base URL : {base_url}")
                        print(f"{Fore.LIGHTYELLOW_EX}🔑 API Key  : {api_key}")
                        print(f"{Fore.LIGHTMAGENTA_EX}🔗 Proxy    : {proxy}")
                        print(f"{Fore.LIGHTGREEN_EX}📝 Answer   : {Fore.LIGHTWHITE_EX}[ {Fore.LIGHTBLUE_EX}{word_count}{Fore.LIGHTWHITE_EX} words ] 🖋️")
                        print(f"{Fore.LIGHTWHITE_EX}=" * 50)
                        
                        return answer
                except Exception as e:
                    retries += 1
                    print(f"{Fore.LIGHTRED_EX}🚨 Error: {str(e)} - (Attempt {retries}/{max_retries})")
                    await asyncio.sleep(5)
        
        return None

async def main():
    bot = ChatBot()
    cycle = 0

    while True:
        cycle += 1
        answered = 0
        failed = 0
        total_questions = len(QUESTIONS)
        
        print(f"{Fore.LIGHTGREEN_EX}🏁 Starting session {cycle} for {total_questions} questions")
        print(f"{Fore.LIGHTWHITE_EX}=" * 50)

        for index, question in enumerate(QUESTIONS, start=1):
            print(f"{Fore.LIGHTBLUE_EX}📝 Question : {question}")
            response = await bot.send_question(question)
            if response:
                answered += 1
            else:
                print(f"{Fore.LIGHTYELLOW_EX}😞 Failed to get an answer.")
                failed += 1
            
            if index < total_questions:
                await asyncio.sleep(random.randint(5, 10))  # Tunggu sebelum pertanyaan berikutnya
        
        print(f"{Fore.LIGHTBLUE_EX}🎯 Session {cycle} completed!")
        print(f"{Fore.LIGHTGREEN_EX}✅ Successfully answered: {answered}")
        print(f"{Fore.LIGHTRED_EX}❌ Not answered: {failed}")
        print(f"{Fore.LIGHTWHITE_EX}=" * 50)
        await asyncio.sleep(5)  # Tunggu sebelum sesi berikutnya

try:
    asyncio.run(main())
except KeyboardInterrupt:
    print(f"{Fore.LIGHTRED_EX}🛑 Program interrupted by the user.")
