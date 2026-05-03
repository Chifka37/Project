# Graph Navigator

**Автор:** Vara Akuseva
**Вариант:** Graph Navigator  
**Дата сдачи:** 03.05.2026  

---

## Описание программы

*"Graph Navigator — это консольное приложение для создания, визуализации и анализа графов различных типов. Позволяет создавать ориентированные, неориентированные и взвешенные графы, добавлять и удалять вершины и рёбра, выполнять обход графа алгоритмами BFS и DFS, находить кратчайший путь между вершинами (BFS для невзвешенных графов, алгоритм Дейкстры для взвешенных), а также сохранять и загружать графы в формате JSON."*

---

## Требования для запуска

- Python 3.8 или выше
- Дополнительные библиотеки **не требуются** (используются только стандартные модули)

---

## Как запустить

```bash
git clone https://github.com/yourusername/graph-navigator.git
cd graph-navigator
python main.py

## Как запустить тесты
bash
python -m unittest discover tests -v
Примеры использования

1. Создание графа
text
============================================================
GRAPH NAVIGATOR - MAIN MENU
============================================================
1. Create New Graph
2. Add Node
3. Add Edge
4. Remove Node
5. Remove Edge
6. View Graph
7. BFS Traversal
8. DFS Traversal
9. Find Shortest Path
10. View Statistics
11. Save Graph
12. Load Graph
13. Exit
============================================================

Enter choice (1-13): 1

Select graph type:
   1. Directed Graph
   2. Undirected Graph
   3. Weighted Graph
Choice (1-3): 1

✓ INFO: Created new directed graph

2. Добавление вершин
text
Enter choice (1-13): 2
Node name: A
✓ INFO: Node 'A' added successfully

Enter choice (1-13): 2
Node name: B
✓ INFO: Node 'B' added successfully

Enter choice (1-13): 2
Node name: C
✓ INFO: Node 'C' added successfully

3. Добавление рёбер
text
Enter choice (1-13): 3
From node: A
To node: B
Weight (optional, default=1): 

✓ INFO: Edge added: A -> B

Enter choice (1-13): 3
From node: B
To node: C
Weight (optional, default=1): 

✓ INFO: Edge added: B -> C

4. Просмотр графа
text
Enter choice (1-13): 6

📊 Graph Info:
   Type: DirectedGraph
   Nodes: 3
   Edges: 2
   Node list: A, B, C

📋 Nodes:
   1. A
   2. B
   3. C

🔗 Edges:
   1. A ---> B
   2. B ---> C

5. BFS обход (без цели)
text
Enter choice (1-13): 7
Start node: A
Target node (optional, press Enter to skip): 

✓ Traversal order: A → B → C

6. BFS поиск пути (с целью)
text
Enter choice (1-13): 7
Start node: A
Target node (optional, press Enter to skip): C

✓ Path found:
   A → B → C

7. DFS обход
text
Enter choice (1-13): 8
Start node: A
Target node (optional, press Enter to skip): 

✓ Traversal order: A → C → B

8. Поиск кратчайшего пути (невзвешенный граф)
text
Enter choice (1-13): 9
Start node: A
Target node: C

✓ Path found:
   A → B → C
   Total distance: 2

9. Взвешенный граф (алгоритм Дейкстры)
text
Enter choice (1-13): 1
Select graph type:
   1. Directed Graph
   2. Undirected Graph
   3. Weighted Graph
Choice (1-3): 3

✓ INFO: Created new weighted graph

Enter choice (1-13): 2
Node name: A
✓ INFO: Node 'A' added successfully

Enter choice (1-13): 2
Node name: B
✓ INFO: Node 'B' added successfully

Enter choice (1-13): 2
Node name: C
✓ INFO: Node 'C' added successfully

Enter choice (1-13): 3
From node: A
To node: B
Weight (optional, default=1): 5

✓ INFO: Edge added: A -[5.0]-> B

Enter choice (1-13): 3
From node: B
To node: C
Weight (optional, default=1): 3

✓ INFO: Edge added: B -[3.0]-> C

Enter choice (1-13): 9
Start node: A
Target node: C

✓ Path found:
   A → B → C
   Total distance: 8.0

10. Удаление вершины
text
Enter choice (1-13): 4
Node name: B

✓ INFO: Node 'B' removed successfully

11. Удаление ребра
text
Enter choice (1-13): 5
From node: A
To node: B

✓ INFO: Edge removed: A -> B

12. Статистика
text
Enter choice (1-13): 10

==================================================
GRAPH STATISTICS
==================================================
   Graph Type: DirectedGraph
   Number of Nodes: 3
   Number of Edges: 2
==================================================

13. Сохранение графа
text
Enter choice (1-13): 11

✓ Graph saved to graph_data.json
✓ INFO: Graph saved successfully

14. Загрузка графа
text
Enter choice (1-13): 12

✓ Loaded DirectedGraph with 3 nodes
✓ INFO: Graph loaded successfully

15. Выход с сохранением
text
Enter choice (1-13): 13
Save graph before exit? (y/n): y

✓ Graph saved to graph_data.json
✓ INFO: Goodbye!

## Примеры ошибочных вводов
Попытка добавить дубликат вершины
text
Enter choice (1-13): 2
Node name: A
✗ ERROR: Node 'A' already exists

Добавление ребра с несуществующей вершиной
text
Enter choice (1-13): 3
From node: A
To node: Z
✗ ERROR: Node 'Z' not found

Отрицательный вес ребра
text
Enter choice (1-13): 3
From node: A
To node: B
Weight (optional, default=1): -5
✗ ERROR: Weight must be positive

Пустое имя вершины
text
Enter choice (1-13): 2
Node name: 
✗ ERROR: Node name cannot be empty

Поиск пути в пустом графе
text
Enter choice (1-13): 9
Start node: A
Target node: B
✗ ERROR: No graph loaded. Create or load a graph first (option 1 or 12)

Некорректный ввод в меню
text
Enter choice (1-13): 99
✗ ERROR: Invalid choice. Please enter 1-13

Тестирование
Запуск тестов:
bash
python -m unittest discover tests -v
Ожидаемый результат:
text
test_add_node_positive ... ok
test_add_duplicate_node_negative ... ok
test_remove_node_positive ... ok
test_remove_nonexistent_node_negative ... ok
test_add_edge_directed_positive ... ok
test_add_edge_undirected_positive ... ok
test_add_edge_weighted_positive ... ok
test_add_edge_with_invalid_weight_negative ... ok
test_add_edge_nonexistent_nodes_negative ... ok
test_remove_edge_positive ... ok
test_bfs_path_found_positive ... ok
test_bfs_path_not_found_negative ... ok
test_bfs_traversal ... ok
test_dfs_path_found_positive ... ok
test_dfs_traversal ... ok
test_shortest_path_unweighted ... ok
test_factory_create_directed ... ok
test_factory_create_invalid_type_negative ... ok

----------------------------------------------------------------------
Ran 18 tests in 0.023s

OK
Структура проекта
text
graph-navigator/
│
├── main.py                 # Единый файл со всем кодом
├── graph_data.json         # JSON файл (создаётся автоматически)
├── test.py                 # Файл с тестами
├── .gitignore              # Игнорируемые файлы
└── README.md               # Документация
