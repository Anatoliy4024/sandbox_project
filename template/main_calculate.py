import logging
import sys
import subprocess


# Функция для передачи данных в калькулятор
def pass_data_to_calculator(person_count, duration):
    subprocess.run(["python", "template/calculate.py", str(person_count), str(duration)])


async def handle_calculate_cost(duration, people_count):
    logging.info(f"Длительность: {duration}, Количество людей: {people_count}")
    pass_data_to_calculator(people_count, duration)
    logging.info(f"Передача данных в калькулятор: Длительность - {duration}, Количество людей - {people_count}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Получаем аргументы, переданные из main.py
    person_count = int(sys.argv[1])
    duration = int(sys.argv[2])

    # Запуск расчета стоимости
    import asyncio

    asyncio.run(handle_calculate_cost(duration, person_count))
