


import aiohttp, asyncio, re, random
from colorama import init, Fore

init(autoreset=True)

# Fungsi untuk memuat API Keys dari file
def load_api_keys(file_path):
    api_keys = []
    try:
        with open(file_path, "r") as file:
            api_keys = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"{Fore.LIGHTRED_EX}🚨 File {Fore.LIGHTWHITE_EX}{file_path} {Fore.LIGHTRED_EX}not found!")
    return api_keys


# Fungsi untuk memuat pertanyaan dari file
def load_questions(file_path):
    questions = []
    try:
        with open(file_path, "r") as file:
            questions = [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"{Fore.LIGHTRED_EX}🚨 File {Fore.LIGHTWHITE_EX}{file_path} {Fore.LIGHTRED_EX}not found!")
    return questions


# Memuat data dari file
API_KEYS = load_api_keys("file_api_keys.txt")
QUESTIONS = load_questions("file_questions.txt")

# Memastikan ada API Key dan daftar pertanyaan yang dimuat
if not API_KEYS or not QUESTIONS:
    print(f"{Fore.LIGHTRED_EX}🚨 API Key and Question list not found. Program is stopping!")
    exit()

# Langsung menetapkan domain
domain_input = "optimize.gaia.domains"
URLS = [domain_input]

print(f"{Fore.LIGHTCYAN_EX}📌 Using domain: {Fore.LIGHTWHITE_EX}{domain_input}")

# Menampilkan domain dan ID yang dipilih oleh pengguna
print(f"{Fore.LIGHTCYAN_EX}🌍 Selected Domain: {Fore.LIGHTWHITE_EX}{URLS[0]}")
print(f"{Fore.LIGHTWHITE_EX}=" * 50)

class ChatBot:
    def __init__(self):
        self.api_key_index = 0

    def get_next_api_key(self):
        """Mengambil API key berikutnya secara bergantian"""
        api_key = API_KEYS[self.api_key_index]
        self.api_key_index = (self.api_key_index + 1) % len(API_KEYS)
        return api_key
    
    async def send_question(self, question: str, max_retries=5):
        """Mengirim pertanyaan ke AI dengan retry terbatas"""
        retries = 0
        while retries < max_retries:  
            api_key = self.get_next_api_key()
            base_url = URLS[0]  # Gunakan URL yang dimasukkan oleh pengguna
            
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
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.post(f"https://{base_url}/v1/chat/completions", headers=headers, json=data, timeout=120) as response:
                        response.raise_for_status()
                        result = await response.json()
                        answer = result["choices"][0]["message"]["content"]
                        
                        print(f"{Fore.LIGHTCYAN_EX}🌍 Base URL : {Fore.LIGHTWHITE_EX}{base_url}")
                        print(f"{Fore.LIGHTYELLOW_EX}🔑 API Key  : {Fore.LIGHTWHITE_EX}{api_key[:10]}*****")  # Masking API Key
                        print(f"{Fore.LIGHTGREEN_EX}💬 Answer   : {Fore.LIGHTWHITE_EX}{answer}")
                        print(f"{Fore.LIGHTWHITE_EX}=" * 50)
                        
                        return answer
                except Exception as e:
                    retries += 1
                    error_message = str(e).strip()
                    if not error_message:  # Jika error message kosong
                        error_message = "Failed to get response."
                    print(f"{Fore.LIGHTRED_EX}🚨 Error    : {Fore.LIGHTWHITE_EX}{error_message} - {Fore.LIGHTYELLOW_EX}(Attempt {retries}/{max_retries})")
                    await countdown_wait(5)
        
        return None  # Jika masih gagal, kembalikan None

async def countdown_next_questions(seconds):
    """Fungsi untuk menampilkan countdown menuju pertanyaan berikutnya"""
    for i in range(seconds, -1, -1):
        print(f"{Fore.LIGHTYELLOW_EX}⏳ Please wait for the next question in {Fore.LIGHTWHITE_EX}{i} {Fore.LIGHTYELLOW_EX}seconds...", end="\r")
        await asyncio.sleep(1)
    print(f"{Fore.LIGHTBLUE_EX}\r\033[K", end="", flush=True)  # Bersihkan baris setelah countdown selesai
    
async def countdown_wait(seconds):
    """Fungsi untuk menampilkan countdown sebelum melanjutkan"""
    for i in range(seconds, -1, -1):
        print(f"{Fore.LIGHTYELLOW_EX}⏳ Please wait for {Fore.LIGHTWHITE_EX}{i} {Fore.LIGHTYELLOW_EX}seconds...", end="\r")
        await asyncio.sleep(1)
    print(f"{Fore.LIGHTBLUE_EX}\r\033[K", end="", flush=True)  # Bersihkan baris setelah countdown selesai


async def main():
    bot = ChatBot()
    cycle = 0

    while True:
        cycle += 1
        answered = 0
        failed = 0
        # random.shuffle(QUESTIONS) # Bisa diaktifkan jika ingin acak pertanyaan
        total_questions = len(QUESTIONS)
        
        print(f"{Fore.LIGHTGREEN_EX}🏁 Starting session {Fore.LIGHTWHITE_EX}{cycle} {Fore.LIGHTGREEN_EX}for {Fore.LIGHTWHITE_EX}{total_questions} {Fore.LIGHTGREEN_EX}{'question' if total_questions == 1 else 'questions'}")
        print(f"{Fore.LIGHTWHITE_EX}=" * 50)

        for index, question in enumerate(QUESTIONS, start=1):
            print(f"{Fore.LIGHTBLUE_EX}📝 Question : {Fore.LIGHTWHITE_EX}{question}")

            response = await bot.send_question(question)

            if response:
                answered += 1
            else:
                print(f"{Fore.LIGHTYELLOW_EX}😞 Failed to get an answer after several attempts. Sorry...")
                print(f"{Fore.LIGHTWHITE_EX}=" * 50)
                failed += 1
            
            if index < total_questions:
                await countdown_next_questions(50)  # Tunggu sebelum pertanyaan berikutnya
        
        print(f"{Fore.LIGHTBLUE_EX}🎯 Session {Fore.LIGHTWHITE_EX}{cycle} {Fore.LIGHTBLUE_EX}completed!")
        print(f"{Fore.LIGHTGREEN_EX}✅ Successfully answered: {Fore.LIGHTWHITE_EX}{answered}")
        print(f"{Fore.LIGHTRED_EX}❌ Not answered: {Fore.LIGHTWHITE_EX}{failed}")
        print(f"{Fore.LIGHTWHITE_EX}=" * 50)
        await countdown_wait(5)  # Tunggu sebelum melanjutkan ke sesi berikutnya


try:
    asyncio.run(main())
except KeyboardInterrupt:
    print(f"{Fore.LIGHTRED_EX}🛑 Program interrupted by the user.")
