from langchain_openai import OpenAI
from langgraph.graph import StateGraph, START, END


# Определение агента-консультанта
def consultant_agent(task_description):
    llm = OpenAI(model="gpt-4o-mini")
    response = llm(task_description)
    return response


# Определение Супервайзера
def supervisor_agent(topic):
    # Создание графа взаимодействия с определением схемы состояния
    graph = StateGraph(state_schema={"result_1": str, "result_2": str})

    # Добавление узлов для каждого агента-консультанта
    graph.add_node("consultant_1",
                   lambda state: {"result_1": consultant_agent(f"Диагностика проблемы по теме: {topic}")})
    graph.add_node("consultant_2", lambda state: {"result_2": consultant_agent(f"Рекомендации по теме: {topic}")})

    # Определение последовательности выполнения
    graph.add_edge(START, "consultant_1")
    graph.add_edge("consultant_1", "consultant_2")
    graph.add_edge("consultant_2", END)

    # Компиляция и выполнение графа
    app = graph.compile(input={}, output=lambda state: state)
    final_state = app.invoke({})

    # Формирование финального отчёта
    report = f"Отчёт по теме '{topic}':\n\n"
    report += f"Диагностика проблемы:\n{final_state['result_1']}\n\n"
    report += f"Рекомендации:\n{final_state['result_2']}\n"

    return report


# Пример использования
topic = "Оптимизация бизнес-процессов"
final_report = supervisor_agent(topic)
print(final_report)
