import json
import matplotlib.pyplot as plt
from datetime import datetime
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import os

# Базовый абстрактный класс для разных типов трат (наследование)
class ExpenseBase(ABC):
    def __init__(self, amount: float, category: str, date: str):
        self._amount = amount  # инкапсуляция
        self._category = category
        self._date = self._validate_date(date)
   
    @property
    def amount(self):
        return self._amount
   
    @amount.setter
    def amount(self, value):
        if value <= 0:
            raise ValueError("Сумма должна быть положительной!")
        self._amount = value
   
    @property
    def category(self):
        return self._category
   
    @property
    def date(self):
        return self._date
   
    def _validate_date(self, date_str: str) -> datetime:
        """Проверка формата даты"""
        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Неверный формат даты! Используйте ГГГГ-ММ-ДД")
   
    @abstractmethod
    def get_type(self) -> str:
        """Абстрактный метод для получения типа расхода"""
        pass
   
    def to_dict(self) -> Dict:
        """Преобразование в словарь для JSON"""
        return {
            "amount": self._amount,
            "category": self._category,
            "date": self._date.strftime("%Y-%m-%d"),
            "type": self.get_type()
        }
   
    @classmethod
    def from_dict(cls, data: Dict):
        """Восстановление объекта из словаря"""
        if data["type"] == "обычный":
            return Expense(data["amount"], data["category"], data["date"])
        elif data["type"] == "крупный":
            return LargeExpense(data["amount"], data["category"], data["date"])
        return Expense(data["amount"], data["category"], data["date"])


# Класс обычных расходов
class Expense(ExpenseBase):
    def get_type(self) -> str:
        return "обычный"
   
    def __str__(self):
        return f"Расход: {self._amount} руб. | Категория: {self._category} | Дата: {self._date.strftime('%Y-%m-%d')}"


# Класс крупных расходов (наследование)
class LargeExpense(ExpenseBase):
    def __init__(self, amount: float, category: str, date: str):
        super().__init__(amount, category, date)
        if amount < 10000:
            raise ValueError("Крупный расход должен быть больше или равен 10000 руб.")
   
    def get_type(self) -> str:
        return "крупный"
   
    def __str__(self):
        return f"КРУПНЫЙ расход: {self._amount} руб. | Категория: {self._category} | Дата: {self._date.strftime('%Y-%m-%d')}"


# Класс для управления расходами
class ExpenseManager:
    def __init__(self, filename: str = "expenses.json"):
        self._filename = filename
        self._expenses: List[ExpenseBase] = []
        self.load_data()
   
    def add_expense(self, amount: float, category: str, date: str, is_large: bool = False):
        """Добавление расхода с проверкой корректности"""
        try:
            if is_large:
                expense = LargeExpense(amount, category, date)
            else:
                expense = Expense(amount, category, date)
            self._expenses.append(expense)
            self.save_data()
            print(f"✓ Расход успешно добавлен!")
            return True
        except ValueError as e:
            print(f"✗ Ошибка: {e}")
            return False
   
    def view_expenses(self):
        """Просмотр всех записей"""
        if not self._expenses:
            print("\nНет записей о расходах.")
            return
       
        print("\n" + "="*60)
        print("СПИСОК ВСЕХ РАСХОДОВ:")
        print("="*60)
        for i, expense in enumerate(self._expenses, 1):
            print(f"{i}. {expense}")
        print("="*60)
   
    def delete_expense(self, index: int):
        """Удаление записи по индексу"""
        try:
            if 1 <= index <= len(self._expenses):
                removed = self._expenses.pop(index - 1)
                self.save_data()
                print(f"✓ Удален расход: {removed}")
            else:
                print(f"✗ Неверный индекс! Введите число от 1 до {len(self._expenses)}")
        except IndexError:
            print("✗ Неверный индекс!")
   
    def filter_by_category(self, category: str) -> List[ExpenseBase]:
        """Фильтрация по категории"""
        filtered = [e for e in self._expenses if e.category.lower() == category.lower()]
        self._display_filtered_results(filtered, f"Категория: {category}")
        return filtered
   
    def filter_by_period(self, start_date: str, end_date: str) -> List[ExpenseBase]:
        """Фильтрация по периоду"""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
           
            filtered = [e for e in self._expenses if start <= e.date <= end]
            self._display_filtered_results(filtered, f"Период: {start_date} - {end_date}")
            return filtered
        except ValueError:
            print("✗ Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return []
   
    def calculate_sum_by_period(self, start_date: str, end_date: str):
        """Подсчёт суммы расходов за период"""
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
           
            total = sum(e.amount for e in self._expenses if start <= e.date <= end)
            print(f"\n{'='*60}")
            print(f"СУММА РАСХОДОВ за период {start_date} - {end_date}: {total:.2f} руб.")
            print(f"{'='*60}")
            return total
        except ValueError:
            print("✗ Неверный формат даты! Используйте ГГГГ-ММ-ДД")
            return 0
   
    def _display_filtered_results(self, filtered: List[ExpenseBase], filter_criteria: str):
        """Отображение отфильтрованных результатов"""
        if not filtered:
            print(f"\nНет расходов по критерию: {filter_criteria}")
            return
       
        print(f"\n{'='*60}")
        print(f"РЕЗУЛЬТАТЫ ФИЛЬТРАЦИИ ({filter_criteria}):")
        print(f"{'='*60}")
        total = 0
        for expense in filtered:
            print(expense)
            total += expense.amount
        print(f"\nИтого: {total:.2f} руб.")
        print(f"{'='*60}")
   
    def plot_expenses_by_category(self):
        """Построение графика расходов по категориям"""
        if not self._expenses:
            print("\nНет данных для построения графика.")
            return
       
        # Агрегация расходов по категориям
        categories = {}
        for expense in self._expenses:
            categories[expense.category] = categories.get(expense.category, 0) + expense.amount
       
        # Построение графика
        plt.figure(figsize=(10, 6))
        plt.bar(categories.keys(), categories.values(), color='skyblue', edgecolor='black')
        plt.xlabel('Категории', fontsize=12)
        plt.ylabel('Сумма расходов (руб.)', fontsize=12)
        plt.title('Расходы по категориям', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.grid(axis='y', alpha=0.3)
       
        # Добавление значений на столбцы
        for i, (category, amount) in enumerate(categories.items()):
            plt.text(i, amount + max(categories.values()) * 0.01, f'{amount:.0f}',
                    ha='center', va='bottom')
       
        plt.tight_layout()
        plt.show()
   
    def save_data(self):
        """Сохранение данных в JSON"""
        try:
            data = [expense.to_dict() for expense in self._expenses]
            with open(self._filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"✗ Ошибка при сохранении данных: {e}")
   
    def load_data(self):
        """Загрузка данных из JSON"""
        if not os.path.exists(self._filename):
            self._expenses = []
            return
       
        try:
            with open(self._filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._expenses = [ExpenseBase.from_dict(item) for item in data]
        except Exception as e:
            print(f"✗ Ошибка при загрузке данных: {e}")
            self._expenses = []


# Функция для проверки ввода суммы
def get_valid_amount():
    while True:
        try:
            amount = float(input("Введите сумму (руб.): "))
            if amount <= 0:
                print("✗ Сумма должна быть положительной!")
                continue
            return amount
        except ValueError:
            print("✗ Введите корректное число!")


# Функция для проверки ввода даты
def get_valid_date(prompt: str = "Введите дату (ГГГГ-ММ-ДД): "):
    while True:
        date_str = input(prompt)
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("✗ Неверный формат даты! Используйте ГГГГ-ММ-ДД (например, 2024-01-15)")


# Главное меню
def main():
    manager = ExpenseManager()
   
    while True:
        print("\n" + "="*60)
        print("ЛИЧНЫЙ ФИНАНСОВЫЙ ПОМОЩНИК")
        print("="*60)
        print("1. Добавить расход")
        print("2. Просмотреть все расходы")
        print("3. Удалить расход")
        print("4. Фильтрация по категории")
        print("5. Фильтрация по периоду")
        print("6. Подсчёт суммы за период")
        print("7. Построить график расходов по категориям")
        print("8. Выход")
        print("="*60)
       
        choice = input("Выберите действие (1-8): ").strip()
       
        if choice == '1':
            print("\n--- ДОБАВЛЕНИЕ РАСХОДА ---")
            amount = get_valid_amount()
            category = input("Введите категорию (например: Еда, Транспорт, Развлечения): ").strip()
            date = get_valid_date()
           
            is_large = input("Это крупный расход? (да/нет): ").strip().lower() == 'да'
            manager.add_expense(amount, category, date, is_large)
       
        elif choice == '2':
            manager.view_expenses()
       
        elif choice == '3':
            if not manager._expenses:
                print("\nНет записей для удаления.")
                continue
            manager.view_expenses()
            try:
                index = int(input("\nВведите номер расхода для удаления: "))
                manager.delete_expense(index)
            except ValueError:
                print("✗ Введите корректный номер!")
       
        elif choice == '4':
            category = input("Введите категорию для фильтрации: ").strip()
            manager.filter_by_category(category)
       
        elif choice == '5':
            print("\n--- ФИЛЬТРАЦИЯ ПО ПЕРИОДУ ---")
            start_date = get_valid_date("Введите начальную дату (ГГГГ-ММ-ДД): ")
            end_date = get_valid_date("Введите конечную дату (ГГГГ-ММ-ДД): ")
            manager.filter_by_period(start_date, end_date)
       
        elif choice == '6':
            print("\n--- ПОДСЧЁТ СУММЫ ЗА ПЕРИОД ---")
            start_date = get_valid_date("Введите начальную дату (ГГГГ-ММ-ДД): ")
            end_date = get_valid_date("Введите конечную дату (ГГГГ-ММ-ДД): ")
            manager.calculate_sum_by_period(start_date, end_date)
       
        elif choice == '7':
            print("\n--- ПОСТРОЕНИЕ ГРАФИКА ---")
            manager.plot_expenses_by_category()
       
        elif choice == '8':
            print("\nДо свидания! Хорошего дня!")
            break
       
        else:
            print("✗ Неверный выбор! Пожалуйста, выберите пункт от 1 до 8.")


if __name__ == "__main__":
    main()
