import os
import sys
import subprocess
import json
from datetime import datetime
from g4f.client import Client
from pathlib import Path

class GPTClient:
    def __init__(self):
        self.client = Client()
        self.memory = []
        self.max_memory = 10  # Максимальное количество сообщений в памяти
        self.system_prompt = """Ты - профессиональный программист на языке Python и Assembly, 
        ты хорошо разбираешься и в других языках программирования, а также отлично понимаешь как работает компьютер, 
        еще ты профессиональный геймер, и хорошо разбираешься в компьютерных играх. 
        Ты очень хорошо разбираешься в оптимизации Windows, знаешь весь Windows реестр наизусть.
        Ты всегда отвечаешь на русском языке.
        Ты всегда помогаешь пользователю с его задачами.
        Ты всегда даешь подробные и понятные объяснения.
        Ты всегда предлагаешь несколько вариантов решения проблемы.
        Ты всегда проверяешь код на ошибки перед отправкой.
        Ты всегда используешь современные практики программирования.
        Ты всегда следуешь принципам безопасности при работе с системой."""
        
        # Создаем директорию для сохранения кода
        self.code_dir = Path("user_data/saved_code")
        self.code_dir.mkdir(parents=True, exist_ok=True)
        self.last_code = None  # Для хранения последнего кода

    def save_code(self, code, language="bat"):
        """Сохраняет код в файл"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.code_dir / f"code_{timestamp}.{language}"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(code)
        return filename

    def execute_command(self, command):
        """Выполняет команду в cmd"""
        try:
            result = subprocess.run(command, shell=True, capture_output=True, text=True)
            return result.stdout if result.returncode == 0 else f"Ошибка: {result.stderr}"
        except Exception as e:
            return f"Ошибка выполнения команды: {str(e)}"

    def get_response(self, message):
        """Получает ответ от GPT с учетом памяти"""
        # Добавляем сообщение в память
        self.memory.append({"role": "user", "content": message})
        
        # Ограничиваем размер памяти
        if len(self.memory) > self.max_memory:
            self.memory = self.memory[-self.max_memory:]
        
        # Формируем сообщения для API
        messages = [{"role": "system", "content": self.system_prompt}] + self.memory
        
        # Получаем ответ
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            web_search=False
        )
        
        # Добавляем ответ в память
        self.memory.append({"role": "assistant", "content": response.choices[0].message.content})
        
        return response.choices[0].message.content

    def run(self):
        """Основной цикл программы"""
        print("Добро пожаловать в GPT-4o-mini!")
        print("Доступные команды:")
        print("  exit - выход из программы")
        print("  save_code - сохранить последний код")
        print("  cmd <команда> - выполнить команду в cmd")
        
        while True:
            try:
                message = input("\nСообщение: ").strip()
                
                if message.lower() == "exit":
                    print("До свидания!")
                    break
                    
                elif message.startswith("cmd "):
                    command = message[4:]
                    result = self.execute_command(command)
                    print(result)
                    
                elif message.startswith("create_file "):
                    path = message[12:]
                    result = self.process_file_operation("create_file", path)
                    print(result)
                    
                elif message.startswith("create_dir "):
                    path = message[11:]
                    result = self.process_file_operation("create_dir", path)
                    print(result)
                    
                elif message.startswith("delete "):
                    path = message[7:]
                    result = self.process_file_operation("delete", path)
                    print(result)
                    
                else:
                    response = self.get_response(message)
                    print("\nОтвет:", response)
                    
                    # Если в ответе есть код, предлагаем сохранить
                    if "```" in response:
                        save = input("\nСохранить код? (y/n): ").lower()
                        if save == "y":
                            # Извлекаем код из ответа
                            code_blocks = response.split("```")
                            for i in range(1, len(code_blocks), 2):
                                code = code_blocks[i].strip()
                                if code:
                                    filename = self.save_code(code)
                                    print(f"Код сохранен в: {filename}")
                    
            except KeyboardInterrupt:
                print("\nПрограмма прервана пользователем")
                break
            except Exception as e:
                print(f"Произошла ошибка: {str(e)}")

if __name__ == "__main__":
    gpt = GPTClient()
    gpt.run()